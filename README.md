# Enterprise FastAPI Backend Template

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3.11-blue.svg?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Testing](https://img.shields.io/badge/testing-pytest-green?style=for-the-badge&logo=pytest)

A modern, production-ready FastAPI backend template featuring enterprise-grade architecture, comprehensive testing, and advanced security features. Built with scalability and developer experience in mind.

[Features](#features) •
[Quick Start](#quick-start) •
[Documentation](#documentation) •
[Development](#development)

</div>

## ✨ Features

### Core Technologies

- 🚀 **FastAPI** - High-performance async web framework
- 🎯 **SQLModel** - Type-annotated database operations
- 🐘 **PostgreSQL** - Robust relational database
- 🐋 **Docker** - Containerized development and deployment
- 🔄 **Alembic** - Database migration management

### Security & Authentication

- 🔐 JWT-based authentication with refresh token rotation
- 🛡️ Role-based access control (RBAC) with granular permissions
- 🔒 Password hashing with Bcrypt and salt
- 🚫 Rate limiting and brute force protection
- 🔍 Security headers and CORS configuration

### Developer Experience

- 🚀 Hot reload for rapid development
- 📝 Auto-generated OpenAPI/Swagger documentation
- 🧪 Comprehensive test suite with pytest fixtures
- 📊 100% type coverage with mypy
- 🎨 Automated code formatting with black and isort
- 🐛 Advanced debugging support

### Production Features

- 📧 Email integration with templates (MJML)
- 📝 Structured logging with correlation IDs
- 🔍 Error tracking with Sentry
- 📊 Metrics and monitoring
- 🚀 CI/CD pipeline ready

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

### Local Development Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

2. Install dependencies:

```bash
uv sync
```

3. Set up environment:

```bash
cp .env.example .env
source .venv/bin/activate
```

4. Start services:

```bash
docker compose watch
```

Visit `http://localhost:8000/docs` for API documentation.

## 📖 Documentation

### Project Structure

```
backend/
├── app/
│   ├── api/           # API routes and endpoints
│   ├── core/          # Core functionality
│   ├── models/        # SQLModel/Pydantic models
│   ├── services/      # Business logic
│   ├── tests/         # Test suite
│   └── main.py        # Application entry point
├── migrations/        # Alembic migrations
└── scripts/          # Utility scripts
```

### API Endpoints

#### Authentication `/api/v1/auth/`

- `POST /login/access-token` - Get access token
- `POST /login/refresh-token` - Refresh access token
- `POST /password-reset` - Request password reset

#### Users `/api/v1/users/`

- `GET /` - List users (admin only)
- `POST /` - Create user
- `GET /me` - Get current user
- `PUT /me` - Update current user

#### Items `/api/v1/items/`

- `GET /` - List items
- `POST /` - Create item
- `GET /{id}` - Get item details
- `PUT /{id}` - Update item
- `DELETE /{id}` - Delete item

## 💻 Development

### Testing

Run test suite:

```bash
# Run all tests
bash ./scripts/test.sh

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest app/tests/api/test_users.py -k test_create_user
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Email Templates

Location: `backend/app/email-templates/`

- Source: `src/*.mjml`
- Built: `build/*.html`

Convert templates:

```bash
# Using VS Code MJML extension
# Or
mjml src/welcome.mjml -o build/welcome.html
```

### Environment Variables

Key configurations in `.env`:

```bash
# API Settings
API_V1_STR=/api/v1
PROJECT_NAME="Your Project Name"
SECRET_KEY=your-secret-key

# Database
POSTGRES_SERVER=localhost
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Email
MAIL_SERVER=smtp.example.com
MAIL_FROM=noreply@example.com

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

## 🔧 Tools & Scripts

### Code Quality

```bash
# Format code
black app/
isort app/

# Type checking
mypy app/

# Lint
ruff check app/
```

### Docker Commands

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

## 📈 Monitoring & Logging

- **Logging**: Structured JSON logging with correlation IDs
- **Metrics**: Prometheus metrics at `/metrics`
- **Tracing**: Sentry integration for error tracking
- **Health**: Health check endpoint at `/health`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Guidelines

- Use conventional commits
- Include ticket number if applicable
- Keep commits focused and atomic

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI framework and community
- SQLModel and its contributors
- All open-source packages used in this project

---

<div align="center">
Made with ❤️ by [Your Name/Organization]
</div>
