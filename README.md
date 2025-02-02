# BitPin Rating System

A Django REST Framework based content rating system that handles high-load scenarios and prevents rating manipulation.

## Features

- Content listing with rating statistics
- User rating system (0-5 stars)
- Anti-manipulation measures
- Rate limiting

## API Endpoints

- `GET /api/content/`: List all content with ratings
- `POST /api/content/{id}/rate/`: Rate a content item

## Performance Considerations

- Redis caching implemented
- Database optimizations
- Rate limiting
- Anti-manipulation measures
