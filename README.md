# Content Manager Application

A comprehensive content management system with TypeScript frontend and Python backend, supporting multi-tenancy, configurable storage, and Azure AD integration.

## Features

- **Multi-tenant Architecture**: Support for multiple organizations with isolated data
- **Configurable Storage**: Support for Azure Storage, GCP Cloud Storage, AWS S3, and local storage
- **Configurable Database**: Support for PostgreSQL, MySQL, SQLite, and MongoDB
- **File Management**: Upload, download, and query files with XML metadata
- **Azure AD Integration**: Role-based access control (RBAC) with Azure Active Directory
- **Modern UI**: React TypeScript frontend with responsive design
- **API-First**: RESTful APIs for all operations
- **Kubernetes Ready**: Helm charts for easy deployment
- **Metadata Storage**: XML metadata stored in database with file location tracking

## Architecture

```
├── backend/           # Python FastAPI backend
├── frontend/          # TypeScript React frontend
├── deployment/        # Kubernetes Helm charts
├── docs/             # Documentation
└── scripts/          # Utility scripts
```

## Technology Stack

### Backend
- **Python 3.11+**
- **FastAPI**: Modern web framework for building APIs
- **SQLAlchemy**: Database ORM with support for multiple databases
- **Azure Identity**: Azure AD integration
- **Storage SDKs**: Azure Storage, Google Cloud Storage, AWS S3
- **Pydantic**: Data validation and serialization

### Frontend
- **TypeScript**
- **React 18**: Modern React with hooks
- **Material-UI**: Component library
- **React Query**: Data fetching and caching
- **Azure MSAL**: Microsoft Authentication Library

### Deployment
- **Kubernetes**: Container orchestration
- **Helm**: Package manager for Kubernetes
- **Docker**: Containerization

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+
- Python 3.11+
- Kubernetes cluster (for production deployment)

### Development Setup

#### Quick Start with Docker
```bash
# Clone the repository
git clone <repository-url>
cd filedeck

# Run the setup script
./scripts/dev-setup.sh --install-deps

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

#### Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd filedeck
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn app.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Environment Configuration**
   - Run `./scripts/dev-setup.sh` to create `.env` files
   - Configure Azure AD application registration
   - Update environment variables with your actual values

### Production Deployment

```bash
# Deploy with Helm
cd deployment
helm install content-manager ./helm-chart
```

## Configuration

### Storage Providers
- Azure Storage Account
- Google Cloud Storage
- AWS S3
- Local File System

### Database Providers
- PostgreSQL (recommended for production)
- MySQL
- SQLite (development only)
- MongoDB

### Environment Variables

See `.env.example` files in backend and frontend directories for all configuration options.

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## CI/CD Pipeline

The project includes comprehensive GitHub Actions workflows:

### 🔄 Automated Workflows

- **Build & Push**: Automatically builds Docker images and pushes to GitHub Container Registry
- **Testing**: Runs comprehensive tests for both backend and frontend
- **Security**: Vulnerability scanning with Trivy and Snyk
- **Release**: Automated releases with changelog generation
- **Dependencies**: Automated dependency updates with Dependabot

### 📦 Docker Images

Images are automatically built and published to GitHub Container Registry:
- `ghcr.io/your-org/filedeck/backend:latest`
- `ghcr.io/your-org/filedeck/frontend:latest`

### 🏷️ Versioning

Create releases by pushing tags:
```bash
git tag v1.0.0
git push origin v1.0.0
```

This will trigger:
- Docker image builds with version tags
- GitHub release with changelog
- Helm chart packaging
- Automatic deployment updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

The CI pipeline will automatically:
- Run tests and code quality checks
- Build Docker images for testing
- Perform security scans
- Validate Helm charts

## License

MIT License 