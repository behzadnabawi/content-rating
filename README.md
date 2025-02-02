# BitPin Rating System

A Django REST Framework based content rating system that handles high-load scenarios and prevents rating manipulation.

## Features

- Content listing with rating statistics
- User rating system (0-5 stars)
- Anti-manipulation measures
- High-performance optimization
- Rate limiting

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Update variables as needed

4. Run migrations:
```bash
python manage.py migrate
```

5. Run development server:
```bash
python manage.py runserver
```

## API Endpoints

- `GET /api/content/`: List all content with ratings
- `POST /api/content/{id}/rate/`: Rate a content item

## Testing

Run tests with:
```bash
python manage.py test
```

## Performance Considerations

- Redis caching implemented
- Database optimizations
- Rate limiting
- Anti-manipulation measures

## Production Deployment

See deployment guide in docs/deployment.md