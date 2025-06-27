# Flutter CRUD Application - Production Docker Setup for Interview

This repository demonstrates a production-ready Docker setup for a Flutter CRUD application with Django backend that works on localhost. The setup is simplified for interview demonstration purposes.

## Architecture

The application consists of:

- **Backend**: Django REST API
- **Frontend**: Flutter web application
- **Database**: PostgreSQL
- **Cache**: Redis
- **Web Server**: Nginx as reverse proxy

## Prerequisites

- Docker and Docker Compose installed

## Quick Start

1. Clone the repository (already done)

2. Deploy the application:

   **On Linux/macOS:**
   ```bash
   ./deploy_local.sh
   ```
   
   **On Windows:**
   ```cmd
   deploy_local.bat
   ```

3. Access the application:

- **Frontend**: http://localhost/ 
- **Backend API**: http://localhost/api/
- **Django Admin**: http://localhost/admin/

## Docker Components

- **docker-compose.prod.yml**: Main configuration file for all services
- **backend/Dockerfile**: Builds the Django backend
- **frontend/Dockerfile**: Builds the Flutter web application
- **nginx/nginx.local.conf**: Nginx configuration for local deployment

## Tech Stack

- **Backend**: Django REST Framework with JWT authentication
- **Frontend**: Flutter Web
- **Database**: PostgreSQL
- **Caching**: Redis
- **Containerization**: Docker & Docker Compose

## Key Features

- Containerized microservices architecture
- Optimized for production use
- Efficient resource utilization
- Proper separation of concerns
- Easy deployment with a single command

## Monitoring

The setup includes health checks for all services.

## Development Environment Setup (Without Docker)

If you prefer to run the application locally without Docker for development, follow these steps:

### Backend Setup

1. **Set up a Python virtual environment**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure local database**:
   - Install PostgreSQL locally or use SQLite for development
   - Create a `.env` file in the backend directory:
```
DEBUG=True
SECRET_KEY=your_dev_secret_key
DB_NAME=flutter_crud_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
SECURE_SSL_REDIRECT=False
```

4. **Run migrations**:
```bash
python manage.py migrate
```

5. **Create a superuser** (optional):
```bash
python manage.py createsuperuser
```

6. **Start the development server**:
```bash
python manage.py runserver
```
   - The API will be available at http://localhost:8000/api/
   - Admin panel at http://localhost:8000/admin/

### Frontend Setup

1. **Install Flutter SDK**:
   - Follow the [official Flutter installation guide](https://flutter.dev/docs/get-started/install)
   - Make sure Flutter is in your PATH and properly set up

2. **Install dependencies**:
```bash
cd frontend
flutter pub get
```

3. **Configure API endpoint**:
   - Update the API endpoint in `lib/services/api_service.dart` to point to your local backend

4. **Run the Flutter application**:
```bash
cd frontend
flutter run -d chrome
```
   - The web app will be available at http://localhost:8080/

### Notes for Development Mode

- The backend server supports hot reloading - changes to Python files will be automatically applied
- Flutter supports hot reload - press "r" in the terminal running flutter to reload changes
- For a smoother development experience, consider using Visual Studio Code with Flutter and Python extensions

## Logs

```bash
# View logs from all containers
docker compose -f docker-compose.prod.yml logs

# View logs from a specific container
docker compose -f docker-compose.prod.yml logs backend
```
