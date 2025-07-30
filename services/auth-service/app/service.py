import grpc
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

from app.proto import auth_service_pb2
from app.proto import auth_service_pb2_grpc
from app.database import User
from app.config import settings
from beanie.exceptions import DocumentNotFound

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService(auth_service_pb2_grpc.AuthServiceServicer):
    def get_password_hash(self, password):
        return pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    async def RegisterUser(self, request, context):
        try:
            hashed_password = self.get_password_hash(request.password)
            user = User(
                username=request.username,
                email=request.email,
                full_name=request.full_name,
                hashed_password=hashed_password
            )
            await user.insert()
            return auth_service_pb2.UserResponse(success=True, message="User registered successfully", user=user.dict())
        except Exception as e:
            return auth_service_pb2.UserResponse(success=False, message=str(e))

    async def LoginUser(self, request, context):
        try:
            user = await User.find_one(User.email == request.email)
            if not user or not self.verify_password(request.password, user.hashed_password):
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Incorrect email or password")
                return auth_service_pb2.LoginUserResponse()

            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={"sub": user.email}, expires_delta=access_token_expires
            )
            refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            refresh_token = self.create_refresh_token(
                data={"sub": user.email}, expires_delta=refresh_token_expires
            )
            return auth_service_pb2.LoginUserResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                user=user.dict()
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_service_pb2.LoginUserResponse()

    async def VerifyToken(self, request, context):
        try:
            payload = jwt.decode(request.token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return auth_service_pb2.VerifyTokenResponse(is_valid=False)
            user = await User.find_one(User.email == email)
            if user is None:
                return auth_service_pb2.VerifyTokenResponse(is_valid=False)
            return auth_service_pb2.VerifyTokenResponse(is_valid=True, user_id=str(user.id), email=user.email)
        except JWTError:
            return auth_service_pb2.VerifyTokenResponse(is_valid=False)

    async def RefreshToken(self, request, context):
        try:
            payload = jwt.decode(request.refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid refresh token")
                return auth_service_pb2.LoginUserResponse()
            
            user = await User.find_one(User.email == email)
            if user is None:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("User not found")
                return auth_service_pb2.LoginUserResponse()

            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={"sub": user.email}, expires_delta=access_token_expires
            )
            return auth_service_pb2.LoginUserResponse(
                access_token=access_token,
                refresh_token=request.refresh_token,
                user=user.dict()
            )
        except JWTError:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid refresh token")
            return auth_service_pb2.LoginUserResponse()

    async def GetUserProfile(self, request, context):
        try:
            user = await User.get(request.user_id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return auth_service_pb2.UserResponse()
            return auth_service_pb2.UserResponse(success=True, user=user.dict())
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            return auth_service_pb2.UserResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_service_pb2.UserResponse()

    async def UpdateUserProfile(self, request, context):
        try:
            user = await User.get(request.user_id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return auth_service_pb2.UserResponse()

            update_data = request.dict(exclude_unset=True)
            await user.update({"$set": update_data})
            return auth_service_pb2.UserResponse(success=True, message="User profile updated successfully", user=user.dict())
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            return auth_service_pb2.UserResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_service_pb2.UserResponse()
