# Django Startup Scaffold

A production-ready Django REST API scaffold for building a job and service marketplace platform. This project provides robust authentication, job posting, service booking, messaging, payments, ratings, analytics, and more, with a modular architecture and Dockerized deployment.

---

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
  - [Docker Deployment (Recommended)](#docker-deployment-recommended)
  - [Manual Setup](#manual-setup)
- [Environment Variables](#environment-variables)
- [Database Seeding](#database-seeding)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Performance & Security](#performance--security)
- [Monitoring & Logging](#monitoring--logging)
- [Contributing](#contributing)
- [License](#license)

---

## Features
- **JWT Authentication**: Registration, login, logout, password reset, email verification
- **Role-based Permissions**: CLIENT, WORKER, SERVICE_PROVIDER, ADMIN
- **Job Marketplace**: Post jobs, apply, hire, manage applications
- **Service Marketplace**: List, book, and manage services
- **Messaging**: Real-time user-to-user messaging
- **Payments**: Multiple payment methods, payment records
- **Ratings & Reviews**: Quality assurance for jobs and services
- **Notifications**: User engagement and alerts
- **Analytics**: Platform usage and performance metrics
- **Admin Panel**: Enhanced with Jazzmin for modern UI
- **API Documentation**: Swagger and Redoc integration
- **Dockerized**: For easy deployment and scaling
- **Celery & Redis**: Background task processing and caching
- **Comprehensive Testing**: Unit, integration, and coverage support

---

## Architecture
- **Backend**: Django 5, Django REST Framework, PostgreSQL, Redis, Celery
- **API**: RESTful, versioned, with consistent response formats
- **Authentication**: JWT (djangorestframework-simplejwt), session, and basic auth
- **Admin**: Jazzmin-enhanced Django admin
- **Containerization**: Docker & docker-compose for all services
- **Task Queue**: Celery for async/background jobs
- **Static Files**: WhiteNoise for static file serving

---

## Project Structure
```
startup_scaffold/
├── accounts/         # User management, authentication, permissions
├── jobs/             # Job posting, applications, hiring
├── services/         # Service marketplace
├── messaging/        # Messaging system
├── payments/         # Payment processing
├── ratings/          # Ratings and reviews
├── analytics/        # Analytics and reporting
├── attendance/       # Attendance tracking
├── shifts/           # Shift management
├── crm/              # Client relationship management
├── notifications/    # Notification system
├── ai_assistant/     # AI assistant features
├── core/             # Core utilities, middleware, base models
├── requirements.txt  # Python dependencies
├── Dockerfile        # Docker build file
├── docker-compose.yml# Docker Compose orchestration
├── .env              # Environment variables
├── SEEDING.md        # Database seeding guide
├── DEPLOYMENT_READINESS_REPORT.md # Deployment checklist
└── ...
```

---

## Setup & Installation

### Docker Deployment (Recommended)
1. **Clone the repository**
   ```bash
git clone <repository-url>
cd django-startup-scaffold/startup_scaffold
```
2. **Configure environment variables**
   ```bash
cp .env.example .env
# Edit .env with your configuration
```
3. **Build and start services**
   ```bash
docker-compose up --build -d
```
4. **Run migrations and create superuser**
   ```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```
5. **Collect static files**
   ```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### Manual Setup
1. **Install dependencies**
   ```bash
pip install -r requirements.txt
```
2. **Configure environment variables** (see below)
3. **Run migrations and create superuser**
   ```bash
python manage.py migrate
python manage.py createsuperuser
```
4. **Collect static files**
   ```bash
python manage.py collectstatic --noinput
```
5. **Start the server**
   ```bash
gunicorn startup_scaffold.wsgi:application --bind 0.0.0.0:8000
```

---

## Environment Variables
Create a `.env` file in the project root. Example:
```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Security
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (for notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## Database Seeding
Populate your database with realistic test data using the custom seeding command. See [SEEDING.md](SEEDING.md) for full details.

- **Basic seeding:**
  ```bash
  python manage.py seed
  ```
- **Custom amounts:**
  ```bash
  python manage.py seed --users 100 --jobs 50 --applications 200
  ```
- **Clear and reseed:**
  ```bash
  python manage.py seed --clear
  ```

---

## API Documentation
- **Swagger UI:** [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- **Redoc:** [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

### Main API Endpoints
- `/api/accounts/` - User registration, login, profile, password reset
- `/api/jobs/` - Job posting, application, hiring
- `/api/services/` - Service listing, booking
- `/api/messaging/` - Conversations, messages
- `/api/payments/` - Payments, payment methods
- `/api/ratings/` - Ratings and reviews
- `/api/analytics/` - Platform analytics
- `/api/notifications/` - User notifications
- `/api/attendance/`, `/api/shifts/`, `/api/crm/`, `/api/ai_assistant/`, `/api/core/` - Additional features

See [DEPLOYMENT_READINESS_REPORT.md](DEPLOYMENT_READINESS_REPORT.md) for a full list of endpoints and integration examples.

---

## Testing
- **Run all tests:**
  ```bash
  python manage.py test
  ```
- **Run specific tests:**
  ```bash
  python manage.py test accounts.tests
  python manage.py test jobs.tests
  # ...
  ```
- **Test coverage:**
  ```bash
  pip install coverage
  coverage run --source='.' manage.py test
  coverage report
  coverage html
  ```

---

## Deployment
- **Production-ready** with Docker, Gunicorn, and environment-based settings
- **Static files** served via WhiteNoise
- **Database**: PostgreSQL (default), can be configured
- **Task queue**: Celery with Redis
- **Health check**: `/api/health/` endpoint

---

## Performance & Security
- **Optimized queries** with select_related, prefetch_related
- **Database indexes** and constraints
- **JWT authentication** and permission-based access
- **Rate limiting** and CORS configuration
- **Input validation** and sanitization
- **HTTPS-ready** (configure in production)

---

## Monitoring & Logging
- **Health monitoring**: `/api/health/`, DB, Redis
- **Structured logging** and error tracking
- **Comprehensive logging configuration** in `core/logging.py`

---

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Create a new Pull Request

---

## License
This project is licensed under the MIT License.

---

For more details, see [SEEDING.md](SEEDING.md) and [DEPLOYMENT_READINESS_REPORT.md](DEPLOYMENT_READINESS_REPORT.md).
