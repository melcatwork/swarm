#!/bin/bash
# Build script for Zeabur deployment
# Builds the frontend and copies it into backend/static for serving

set -e  # Exit on error

echo "=== Building Swarm TM for Zeabur ==="

# Build frontend
echo "Step 1: Building frontend..."
cd frontend
npm ci
npm run build
cd ..

# Copy frontend build to backend static directory
echo "Step 2: Copying frontend build to backend..."
mkdir -p backend/static
cp -r frontend/dist/* backend/static/

echo "Step 3: Build complete!"
echo "Frontend built and copied to backend/static"
ls -la backend/static/

echo "=== Build successful ==="
