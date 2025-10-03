# FastAPI Backend API

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Latest-green.svg)](https://mongodb.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

A production-ready FastAPI backend API built with Clean Architecture principles, featuring multi-tenancy, comprehensive user management, AI integration, and cloud storage support.

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Pull and run the container
docker run -d \
  --name fastapi-backend \
  -p 8000:8000 \
  -e MONGO_URI=mongodb://your-mongo-host:27017 \
  -e JWT_SECRET=your-secret-key \
  your-registry/fastapi-backend:latest

# Access the API
curl http://localhost:8000/health
```

### Environment Variables

```bash
# Required Environment Variables
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=your_database
JWT_SECRET=your-jwt-secret-key
REFRESH_TOKEN_SECRET=your-refresh-secret-key

# Optional Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=SecurePassword123!
```

## ✨ Key Features

### 🔐 Authentication & Authorization
- **JWT Authentication** with access and refresh tokens
- **Role-Based Access Control (RBAC)** with granular permissions
- **Multi-factor Authentication** support
- **Password Reset** with email verification
- **Session Management** with automatic token refresh

### 🏢 Multi-Tenant Architecture
- **Flexible Multi-Tenancy** with header or subdomain strategies
- **Tenant Isolation** with secure data separation
- **Dynamic Tenant Creation** with automated setup
- **Subdomain Management** with availability checking
- **Tenant-Scoped Permissions** and role assignments

### 👥 User Management
- **Complete User CRUD** operations with validation
- **User Profile Management** with image upload support
- **Account Activation/Deactivation** workflows
- **Role Assignment** within tenant contexts
- **User Search and Filtering** capabilities

### 🎭 Role & Permission System
- **Dynamic Role Creation** with custom permissions
- **Permission Matrix** for fine-grained access control
- **Role Inheritance** and hierarchical permissions
- **Runtime Permission Checking** with decorators
- **Audit Trail** for role and permission changes

### 🤖 AI Integration
- **Local AI Models** integration with Ollama support
- **Real-time Streaming** responses for chat interfaces
- **Conversation History** with persistent storage
- **Multiple Model Support** with dynamic switching
- **LangChain Integration** for advanced AI workflows

### ☁️ Cloud Storage
- **Azure Blob Storage** native integration
- **AWS S3 Compatible** storage support
- **File Upload Management** with validation and processing
- **Storage Provider Abstraction** for easy switching
- **Secure File Access** with signed URLs

### 📧 Email System
- **Async Email Sending** with FastAPI-Mail
- **Template Engine** for dynamic email content
- **Background Processing** with Celery integration
- **SMTP Configuration** with multiple provider support
- **Email Verification** workflows

### ⚡ Background Processing
- **Celery Integration** with Redis broker
- **Async Task Processing** for heavy operations
- **Task Monitoring** with Flower dashboard
- **Retry Logic** and error handling
- **Scheduled Tasks** support

## 🏗️ Architecture

### Clean Architecture Layers

```
api/
├── domain/              # Business Logic Layer
│   ├── entities/       # Core business entities
│   ├── dtos/           # Data transfer objects
│   ├── interfaces/     # Abstract interfaces
│   └── enum/           # Domain enums and constants
├── usecases/           # Application Business Rules
│   ├── auth_service.py
│   ├── user_service.py
│   ├── tenant_service.py
│   ├── role_service.py
│   └── local_ai_service.py
├── interfaces/         # Interface Adapters
│   ├── api_controllers/ # REST API endpoints
│   ├── middlewares/    # HTTP middlewares
│   └── security/       # Authentication handlers
├── infrastructure/     # Frameworks & Drivers
│   ├── persistence/    # Database implementations
│   ├── externals/      # Third-party integrations
│   ├── messaging/      # Message brokers
│   └── cache/          # Caching implementations
└── common/             # Shared Utilities
    ├── exceptions/     # Custom exceptions
    ├── utils/          # Helper functions
    └── dtos/           # Common DTOs
```

### Technology Stack

- **Framework**: FastAPI 0.116+ with Pydantic v2
- **Database**: MongoDB with Beanie ODM for async operations
- **Cache**: Redis for session storage and caching
- **Background Tasks**: Celery with Redis broker
- **Authentication**: JWT with PyJWT
- **AI**: LangChain with Ollama integration
- **Storage**: Azure Blob Storage, AWS S3 compatible
- **Email**: FastAPI-Mail with async SMTP
- **Security**: Passlib for password hashing
- **Dependency Injection**: Punq container
- **Testing**: Pytest with async support

## 🔌 API Endpoints

### Authentication
```
POST   /api/v1/auth/login          # User login
POST   /api/v1/auth/refresh        # Refresh access token
POST   /api/v1/auth/logout         # User logout
POST   /api/v1/auth/register       # User registration
POST   /api/v1/auth/forgot-password # Password reset request
```

### User Management
```
GET    /api/v1/users               # List users (paginated)
POST   /api/v1/users               # Create new user
GET    /api/v1/users/{id}          # Get user details
PUT    /api/v1/users/{id}          # Update user
DELETE /api/v1/users/{id}          # Delete user
POST   /api/v1/users/{id}/avatar   # Upload user avatar
```

### Tenant Management
```
GET    /api/v1/tenants             # List tenants
POST   /api/v1/tenants             # Create tenant
GET    /api/v1/tenants/{id}        # Get tenant details
PUT    /api/v1/tenants/{id}        # Update tenant
DELETE /api/v1/tenants/{id}        # Delete tenant
GET    /api/v1/tenants/search      # Search tenants by name
```

### Role & Permissions
```
GET    /api/v1/roles               # List roles
POST   /api/v1/roles               # Create role
PUT    /api/v1/roles/{id}          # Update role
DELETE /api/v1/roles/{id}          # Delete role
GET    /api/v1/permissions         # List all permissions
```

### AI Integration
```
GET    /api/v1/ai/models           # List available AI models
POST   /api/v1/ai/ask              # Send AI query (streaming)
GET    /api/v1/ai/history          # Get conversation history
POST   /api/v1/ai/clear-history    # Clear conversation history
```

### Storage Management
```
GET    /api/v1/storage             # Get storage settings
PUT    /api/v1/storage             # Update storage settings
GET    /api/v1/storage/available   # List available providers
POST   /api/v1/upload              # Upload file
```

### System
```
GET    /health                     # Health check endpoint
GET    /docs                       # OpenAPI documentation
GET    /redoc                      # ReDoc documentation
```

## 🐳 Docker Deployment

### Build Image

```dockerfile
FROM python:3.13-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /api
COPY . /api/
RUN uv sync --frozen --no-cache

# Install system dependencies
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

USER appuser
EXPOSE 8000

CMD ["uv", "run", "fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.9'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGO_URI=mongodb://mongodb:27017
      - REDIS_HOST=redis
      - JWT_SECRET=your-secret-key
    depends_on:
      - mongodb
      - redis
  
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
  
  redis:
    image: redis:latest
    ports:
      - "6379:6379"

volumes:
  mongodb_data:
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGO_URI` | MongoDB connection string | - | ✅ |
| `MONGO_DB_NAME` | Database name | - | ✅ |
| `JWT_SECRET` | JWT signing secret | - | ✅ |
| `REFRESH_TOKEN_SECRET` | Refresh token secret | - | ✅ |
| `REDIS_HOST` | Redis server host | localhost | ❌ |
| `REDIS_PORT` | Redis server port | 6379 | ❌ |
| `ADMIN_EMAIL` | Default admin email | admin@example.com | ❌ |
| `ADMIN_PASSWORD` | Default admin password | - | ❌ |
| `SMTP_HOST` | SMTP server host | - | ❌ |
| `SMTP_PORT` | SMTP server port | 587 | ❌ |
| `MULTI_TENANCY_STRATEGY` | Tenant strategy | header | ❌ |
| `HOST_MAIN_DOMAIN` | Main domain for subdomains | - | ❌ |

### Multi-Tenancy Configuration

```bash
# Header-based tenancy (recommended for APIs)
MULTI_TENANCY_STRATEGY=header

# Subdomain-based tenancy (for web applications)
MULTI_TENANCY_STRATEGY=subdomain
HOST_MAIN_DOMAIN=yourdomain.com

# Single tenant mode
MULTI_TENANCY_STRATEGY=none
```

### AI Configuration

```bash
# Ollama Configuration (for local AI models)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODELS=llama2,codellama,mistral

# OpenAI Configuration (optional)
OPENAI_API_KEY=your-openai-key
```

### Storage Configuration

```bash
# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_STORAGE_CONTAINER=your-container

# AWS S3 Compatible
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=your-bucket
AWS_S3_REGION=us-east-1
```

## 🚀 Development

### Local Development

```bash
# Install dependencies
uv sync

# Start development server
uv run fastapi dev

# Run with auto-reload
uv run fastapi dev --reload

# Run background worker
uv run celery -A api.infrastructure.messaging.celery_worker worker --loglevel=info

# Monitor tasks with Flower
uv run celery -A api.infrastructure.messaging.celery_worker flower
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=api

# Run specific test file
uv run pytest tests/interfaces/test_user_endpoint.py
```

## 📊 Monitoring & Observability

### Health Checks

```bash
# API Health
GET /health

# Database Health
GET /health/db

# Redis Health
GET /health/cache
```

### Logging

- **Structured Logging** with colorlog
- **Request/Response Logging** with correlation IDs
- **Error Tracking** with detailed stack traces
- **Performance Metrics** for API endpoints

### Background Task Monitoring

```bash
# Flower Dashboard
http://localhost:5555

# Celery Status
celery -A api.infrastructure.messaging.celery_worker status
```

## 🔒 Security Features

### Authentication Security
- **JWT with RS256** signing (configurable)
- **Refresh Token Rotation** for enhanced security
- **Password Hashing** with bcrypt
- **Rate Limiting** on auth endpoints
- **CORS Configuration** for cross-origin requests

### Data Security
- **SQL Injection Prevention** with parameterized queries
- **Input Validation** with Pydantic models
- **Output Sanitization** for API responses
- **Secure Headers** with security middlewares
- **Environment Variable Protection** for secrets

### Multi-Tenant Security
- **Data Isolation** between tenants
- **Tenant-Scoped Queries** automatic filtering
- **Permission Boundaries** preventing cross-tenant access
- **Audit Logging** for tenant operations

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Authentication Examples

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}'

# Use JWT Token
curl -X GET "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Multi-tenant request with header
curl -X GET "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "X-Tenant-ID: tenant-uuid"
```

## 🤝 Contributing

1. **Clean Architecture**: Follow the established layer separation
2. **Type Safety**: Use Pydantic models for all data validation
3. **Testing**: Add tests for new features and endpoints
4. **Documentation**: Update API documentation for changes
5. **Security**: Follow security best practices for new code

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Production Ready**: This API is designed for production use with comprehensive security, scalability, and monitoring features built-in.