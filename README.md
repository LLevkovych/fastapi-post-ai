# FastPostAI

A modern FastAPI-based social media platform with AI-powered content moderation and automatic reply functionality.

## Features

- **User Authentication**: JWT-based authentication with registration and login
- **Post Management**: Create, read, update, and delete posts
- **Comment System**: Full CRUD operations for comments
- **AI Content Moderation**: Google AI-powered content filtering
- **Auto-Reply System**: Automatic responses to comments using AI
- **Analytics**: Daily comment breakdown and moderation statistics
- **Docker Support**: Full containerization with Docker Compose

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Alembic
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: JWT with bcrypt password hashing
- **AI Services**: Google Generative AI, OpenAI
- **Background Tasks**: Celery with Redis
- **Testing**: Pytest with async support
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Google AI API Key (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FastPostAI
   ```

2. **Set up environment variables**
   ```bash
   cp env.sample .env
   # Edit .env with your configuration
   ```

3. **Run with Docker**
   ```bash
   docker-compose up -d
   ```

4. **Access the API**
   - API Documentation: http://localhost:8001/docs
   - Health Check: http://localhost:8001/health

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token

### Posts
- `GET /posts/` - List posts with pagination
- `POST /posts/` - Create new post (with AI moderation)
- `GET /posts/{id}` - Get specific post
- `PUT /posts/{id}` - Update post
- `DELETE /posts/{id}` - Delete post

### Comments
- `GET /posts/{id}/comments/` - List comments for post
- `POST /posts/{id}/comments/` - Create comment (with auto-reply)
- `PUT /posts/{id}/comments/{comment_id}` - Update comment
- `DELETE /posts/{id}/comments/{comment_id}` - Delete comment

### Analytics
- `GET /analytics/comments-daily-breakdown` - Daily comment statistics

## AI Features

### Content Moderation
- Automatic content filtering using Google AI
- Configurable moderation settings
- Content blocking for inappropriate material

### Auto-Reply System
- AI-generated responses to comments
- Configurable delay and enable/disable per post
- Relevant context-aware replies

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_moderation.py

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run end-to-end tests
python test_basic_functionality.py
```

### Test Results
- **Code Coverage:** 51%
- **Unit Tests:** 60% success rate
- **End-to-End Tests:** 100% success rate
- **API Functionality:** 100% operational

See [TEST_RESULTS.md](TEST_RESULTS.md) for detailed test results.

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Configuration

Key environment variables:
- `GOOGLE_AI_API_KEY`: Google AI API key for moderation
- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: Database connection string
- `MODERATION_ENABLED`: Enable/disable AI moderation
- `DEFAULT_AUTO_REPLY_DELAY`: Default delay for auto-replies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License 