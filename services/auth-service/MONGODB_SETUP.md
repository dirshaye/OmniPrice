# MongoDB Atlas Setup Checklist

## 🎯 Quick Setup Steps

### 1. Create MongoDB Atlas Account
- [ ] Go to [https://www.mongodb.com/atlas](https://www.mongodb.com/atlas)
- [ ] Sign up for free account
- [ ] Verify your email

### 2. Create a Cluster
- [ ] Click "Create" to build a cluster
- [ ] Choose **M0 Sandbox** (Free Forever)
- [ ] Select cloud provider (AWS recommended)
- [ ] Choose region closest to you
- [ ] Name your cluster (e.g., "omnipricex-cluster")
- [ ] Click "Create Cluster" (takes 2-3 minutes)

### 3. Create Database User
- [ ] Go to "Database Access" in left sidebar
- [ ] Click "Add New Database User"
- [ ] Choose "Password" authentication
- [ ] Enter username: `omnipricex_user`
- [ ] Generate secure password (save it!)
- [ ] Set permissions to "Read and write to any database"
- [ ] Click "Add User"

### 4. Configure Network Access
- [ ] Go to "Network Access" in left sidebar
- [ ] Click "Add IP Address"
- [ ] For development, click "Allow Access from Anywhere" (0.0.0.0/0)
- [ ] For production, add specific IP addresses
- [ ] Click "Confirm"

### 5. Get Connection String
- [ ] Go to "Clusters" in left sidebar
- [ ] Click "Connect" on your cluster
- [ ] Choose "Connect your application"
- [ ] Select "Python" and version "3.6 or later"
- [ ] Copy the connection string
- [ ] It looks like: `mongodb+srv://omnipricex_user:<password>@omnipricex-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority`

### 6. Configure Environment
- [ ] Open `/home/dre/Desktop/Github/OmniPriceX/services/auth-service/.env`
- [ ] Replace `MONGODB_URL` with your connection string
- [ ] Replace `<password>` with your actual database user password
- [ ] Add database name: `...mongodb.net/omnipricex_auth?retryWrites=true&w=majority`

### 7. Generate Secret Key
```bash
# Generate a secure secret key
openssl rand -hex 32
```
- [ ] Copy the generated key
- [ ] Replace `SECRET_KEY` in `.env` file

### 8. Test Connection
```bash
# Install dependencies
pip install -r requirements.txt

# Test MongoDB connection
python setup_mongodb.py
```

## 🔧 Example Configuration

Your `.env` file should look like:
```env
MONGODB_URL=mongodb+srv://your-username:your-password@your-cluster.xxxxx.mongodb.net/omnipricex_auth?retryWrites=true&w=majority
DATABASE_NAME=omnipricex_auth
SECRET_KEY=a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
```

## ⚠️ Important Notes

### Security Best Practices:
- **Never commit `.env` file to git**
- **Use strong passwords for database users**
- **Restrict IP access in production**
- **Rotate secrets regularly**

### Database Organization:
- **Database Name**: `omnipricex_auth` (for auth service)
- **Collections**: `users`, `refreshtokens` (auto-created)
- **Future databases**: `omnipricex_products`, `omnipricex_pricing`

### Connection Troubleshooting:
1. **Authentication failed**: Check username/password
2. **Connection timeout**: Check IP whitelist
3. **Database not found**: Database is created automatically
4. **SSL errors**: Ensure connection string has correct parameters

## 🚀 Ready to Test?

Once you've completed the checklist:
```bash
# Test MongoDB connection
python setup_mongodb.py

# If successful, start auth service
python run.py
```

Your auth service will be available at: http://localhost:8001

## 📱 What's Next?

After MongoDB setup:
1. ✅ Test connection with `setup_mongodb.py`
2. ✅ Start auth service with `python run.py`
3. ✅ Test API with `python demo.py`
4. ✅ View docs at http://localhost:8001/api/v1/docs
5. ✅ Integrate with frontend applications
