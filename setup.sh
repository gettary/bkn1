#!/bin/bash

# BKN1 Assessment System Setup Script

echo "🚀 Setting up BKN1 Assessment System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
chmod 755 uploads

# Generate random secrets if not set
if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY=$(openssl rand -hex 32)
    echo "🔑 Generated SECRET_KEY: $SECRET_KEY"
fi

# Pull latest images
echo "📦 Pulling Docker images..."
docker compose pull

# Build and start services
echo "🏗️ Building and starting services..."
docker compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
docker compose ps

# Show access information
echo ""
echo "🎉 BKN1 Assessment System is ready!"
echo ""
echo "📱 Access URLs:"
echo "   Main Application: http://localhost"
echo "   PgAdmin:         http://localhost:5050"
echo "   Metabase:        http://localhost:3001"
echo ""
echo "👥 Default Users:"
echo "   Admin:     username: admin,     password: admin123"
echo "   Moderator: username: moderator, password: admin123"
echo "   User:      username: user1,     password: admin123"
echo ""
echo "📋 Useful Commands:"
echo "   View logs:     docker compose logs -f"
echo "   Stop system:   docker compose down"
echo "   Restart:       docker compose restart"
echo "   Clean up:      docker compose down -v"
echo ""
echo "✨ Happy assessing!"