# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package.json and package-lock.json (if available)
# Note: this Dockerfile is built with `frontend/` as the build context.
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Install missing peer dependencies
RUN npm install ajv@latest --legacy-peer-deps

# Copy source code
COPY . .

# Build the application
ENV GENERATE_SOURCEMAP=false
ENV CI=false
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
