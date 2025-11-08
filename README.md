# AutoWeb Outreach AI

Automated lead generation platform that discovers UK businesses with underperforming websites, evaluates them using Google Lighthouse, and generates AI-powered website previews personalized with actual business data.

## Overview

AutoWeb Outreach AI transforms lead generation for web development agencies by:
- **Automated Discovery**: Scrapes UK business directories (Checkatrade, Yell) to find prospects
- **Objective Evaluation**: Uses Google Lighthouse to score website performance, SEO, and accessibility
- **AI-Powered Previews**: Generates personalized website templates using GPT-4 for businesses scoring < 70%
- **Visual Proof-of-Concept**: Provides side-by-side comparisons showing transformation potential

## Prerequisites

- **Python**: 3.11+ (backend)
- **Node.js**: 18+ (frontend)
- **Docker**: For PostgreSQL and Redis services
- **Git**: For version control

## Project Structure

```
AutoWeb_Outreach_AI/
├── backend/              # Python FastAPI application
│   ├── app/
│   │   ├── main.py      # FastAPI entry point
│   │   ├── config.py    # Configuration management
│   │   ├── database.py  # Database setup
│   │   ├── models/      # SQLAlchemy ORM models
│   │   ├── routes/      # API endpoints
│   │   ├── services/    # Business logic
│   │   └── schemas/     # Pydantic schemas
│   ├── tests/           # Test suite
│   ├── requirements.txt # Python dependencies
│   └── .env.example     # Environment variables template
├── frontend/            # Next.js 14+ application
│   ├── app/            # App Router pages
│   ├── components/     # React components
│   ├── lib/            # Utility functions
│   ├── package.json    # Node dependencies
│   └── .env.example    # Frontend environment variables
├── docs/               # Documentation (PRD, epics, stories)
├── docker-compose.yml  # Docker services configuration
└── README.md          # This file
```

## Setup Instructions

### 1. Clone Repository

```bash
git clone <repository-url>
cd AutoWeb_Outreach_AI
```

### 2. Start Docker Services

Start PostgreSQL and Redis:

```bash
docker-compose up -d
```

Verify services are running:

```bash
docker-compose ps
```

### 3. Backend Setup

#### Install Python Dependencies

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### Configure Environment

```bash
cp .env.example .env
# Edit .env and set your OpenAI API key and other configuration
```

#### Run Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

### 4. Frontend Setup

#### Install Node Dependencies

```bash
cd frontend
npm install
```

#### Configure Environment

```bash
cp .env.example .env.local
# Edit .env.local if needed (default API URL is http://localhost:8000)
```

#### Run Frontend

```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

## Development Commands

### Backend

```bash
# Run development server
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black app/

# Lint
flake8 app/
```

### Frontend

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint
npm run lint
```

### Docker

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild services
docker-compose up -d --build
```

## Architecture Overview

### Backend (Python FastAPI)

- **FastAPI**: Modern async web framework for building APIs
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database for storing businesses, evaluations, and templates
- **Redis**: Message broker for Celery background tasks
- **Celery**: Distributed task queue for scraping, evaluation, and AI generation
- **Selenium**: Web scraping UK business directories
- **OpenAI GPT-4**: AI-powered website template generation

### Frontend (Next.js 14+)

- **Next.js**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library

### Database Schema

- `businesses`: Business contact and website data
- `evaluations`: Lighthouse scores and performance metrics
- `evaluation_problems`: Specific issues identified
- `templates`: AI-generated HTML templates
- `users`: Authentication and user management

## Environment Variables

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql://postgres:postgres@localhost:5432/autoweb_db |
| REDIS_URL | Redis connection string | redis://localhost:6379/0 |
| JWT_SECRET | Secret key for JWT tokens | (must be set) |
| OPENAI_API_KEY | OpenAI API key for GPT-4 | (must be set) |
| DEBUG | Enable debug mode | True |

### Frontend (.env.local)

| Variable | Description | Default |
|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend API URL | http://localhost:8000 |

## Key Features

1. **Business Discovery**: Automated scraping from UK directories with geographic and niche filtering
2. **Website Evaluation**: Google Lighthouse CLI integration for objective performance scoring
3. **AI Template Generation**: GPT-4 creates personalized, responsive website templates
4. **Business Cards UI**: Professional grid display with search, filtering, and score indicators
5. **Template Preview**: Side-by-side comparison with mobile/desktop toggle
6. **Improvements Tracking**: Detailed analysis of enhancements in AI-generated templates

## API Endpoints

### Health Check
- `GET /api/health` - Check API status

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### Businesses
- `GET /api/businesses` - List businesses (with pagination and filters)
- `GET /api/businesses/{id}` - Get business details
- `POST /api/businesses` - Create business (manual entry)

### Scraping
- `POST /api/scraping-jobs` - Start scraping job
- `GET /api/scraping-jobs/{id}` - Check job status

### Evaluations
- `GET /api/businesses/{id}/evaluation` - Get evaluation results
- `POST /api/evaluations` - Trigger website evaluation

### Templates
- `GET /api/businesses/{id}/templates` - Get all template variants
- `GET /api/templates/{id}/preview` - Preview template HTML

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

(Deployment instructions to be added in later stories)

## Contributing

1. Create feature branch from `main`
2. Make changes following project structure and coding standards
3. Write tests for new functionality
4. Submit pull request with description of changes

## License

Proprietary - All rights reserved

## Support

For issues or questions, please contact the development team.
