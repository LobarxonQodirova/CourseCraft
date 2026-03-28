# CourseCraft - Course Creation & Publishing Platform

A production-grade course creation and publishing platform for content creators. Build, publish, and sell online courses with drag-and-drop course building, multimedia lessons, drip content scheduling, student engagement analytics, custom landing pages, flexible pricing tiers, coupons, and an affiliate program.

## Architecture

- **Backend:** Django 5.x + Django REST Framework
- **Frontend:** Next.js 14 (App Router) with React 18
- **Database:** PostgreSQL 16
- **Cache / Broker:** Redis 7
- **Task Queue:** Celery 5
- **Reverse Proxy:** Nginx
- **Containerization:** Docker & Docker Compose

## Features

| Area | Details |
|---|---|
| Course Builder | Drag-and-drop modules and lessons, reorder with position tracking |
| Multimedia Lessons | Video (upload/embed), rich text, PDF attachments |
| Drip Content | Time-based, enrollment-based, or prerequisite-based drip rules |
| Student Analytics | Engagement metrics, completion rates, funnel analysis |
| Landing Pages | Per-course customizable landing pages with section editor |
| Pricing | Multiple tiers per course, bundles, percentage/fixed coupons |
| Payments | Stripe integration, creator payouts, refund management |
| Affiliates | Per-course affiliate programs, trackable links, commission payouts |

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/your-org/coursecraft.git
cd coursecraft

# Copy environment variables
cp .env.example .env
# Edit .env with your own secrets

# Build and start all services
docker compose up --build -d

# Run backend migrations
docker compose exec backend python manage.py migrate

# Create a superuser
docker compose exec backend python manage.py createsuperuser

# Seed sample data (optional)
docker compose exec backend python manage.py loaddata sample_data
```

The application will be available at:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api/
- **Admin Panel:** http://localhost:8000/admin/
- **API Documentation:** http://localhost:8000/api/docs/

## Project Structure

```
coursecraft/
├── backend/
│   ├── config/              # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── celery.py
│   ├── apps/
│   │   ├── accounts/        # User models, auth, profiles
│   │   ├── courses/         # Course, Module, Lesson management
│   │   ├── enrollments/     # Enrollment, progress, certificates
│   │   ├── pricing/         # Plans, coupons, bundles
│   │   ├── payments/        # Stripe payments, payouts, refunds
│   │   ├── landing_pages/   # Course landing page builder
│   │   ├── analytics/       # Views, engagement, funnels
│   │   ├── drip_content/    # Drip scheduling and rules
│   │   └── affiliates/      # Affiliate program management
│   ├── utils/               # Shared utilities
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # Reusable React components
│   │   ├── lib/             # API client, auth helpers, utils
│   │   ├── context/         # React context providers
│   │   ├── hooks/           # Custom React hooks
│   │   └── styles/          # Global CSS
│   ├── package.json
│   ├── next.config.js
│   └── Dockerfile
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - JWT token login
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Courses
- `GET /api/courses/` - List published courses
- `POST /api/courses/` - Create a course (creator)
- `GET /api/courses/{slug}/` - Course detail
- `PUT /api/courses/{id}/` - Update course
- `POST /api/courses/{id}/modules/` - Add module
- `POST /api/modules/{id}/lessons/` - Add lesson

### Enrollments
- `POST /api/enrollments/` - Enroll in a course
- `POST /api/enrollments/{id}/progress/` - Update lesson progress
- `GET /api/enrollments/my/` - Current user enrollments

### Payments
- `POST /api/payments/checkout/` - Create Stripe checkout session
- `POST /api/payments/webhook/` - Stripe webhook handler

### Analytics
- `GET /api/analytics/course/{id}/overview/` - Course analytics overview
- `GET /api/analytics/course/{id}/engagement/` - Engagement metrics
- `GET /api/analytics/creator/revenue/` - Revenue analytics

### Affiliates
- `POST /api/affiliates/programs/` - Create affiliate program
- `GET /api/affiliates/links/` - List affiliate links
- `GET /api/affiliates/commissions/` - Commission report

## Environment Variables

See `.env.example` for the full list of required and optional environment variables.

## Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
docker compose exec backend python manage.py test

# Frontend tests
docker compose exec frontend npm test
```

## Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Configure a proper `SECRET_KEY`
3. Set up SSL certificates in nginx
4. Configure Stripe live keys
5. Set up a proper PostgreSQL backup strategy
6. Configure email backend for transactional emails

## License

MIT License. See LICENSE for details.
