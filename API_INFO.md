# FastPostAI API Documentation

## Overview

FastPostAI is a modern social media platform API built with FastAPI, featuring AI-powered content moderation and automatic reply functionality.

## Base URL

```
http://localhost:8001
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true
}
```

#### Login User
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_active": true
  }
}
```

#### Refresh Token
```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Posts

#### List Posts
```http
GET /posts/?page=1&page_size=10&author_id=1
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 10, max: 100)
- `author_id` (optional): Filter by author ID

**Response:**
```json
{
  "posts": [...],
  "total": 25,
  "page": 1,
  "page_size": 10,
  "pages": 3
}
```

#### Create Post
```http
POST /posts/
```

**Request Body:**
```json
{
  "title": "My Post Title",
  "content": "Post content here...",
  "auto_reply_enabled": true,
  "auto_reply_delay": 60
}
```

**Features:**
- AI content moderation (if enabled)
- Auto-reply configuration

#### Get Post
```http
GET /posts/{post_id}
```

#### Update Post
```http
PUT /posts/{post_id}
```

**Request Body:**
```json
{
  "title": "Updated Title",
  "content": "Updated content...",
  "auto_reply_enabled": false
}
```

#### Delete Post
```http
DELETE /posts/{post_id}
```

### Comments

#### List Comments
```http
GET /posts/{post_id}/comments/?page=1&page_size=50&include_blocked=false
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 50, max: 100)
- `include_blocked` (optional): Include blocked comments (default: false)

#### Create Comment
```http
POST /posts/{post_id}/comments/
```

**Request Body:**
```json
{
  "content": "Comment content here..."
}
```

**Features:**
- AI content moderation
- Automatic reply scheduling (if enabled on post)

#### Update Comment
```http
PUT /posts/{post_id}/comments/{comment_id}
```

#### Delete Comment
```http
DELETE /posts/{post_id}/comments/{comment_id}
```

### Analytics

#### Daily Comment Breakdown
```http
GET /analytics/comments-daily-breakdown?date_from=2024-01-01&date_to=2024-01-31
```

**Query Parameters:**
- `date_from` (required): Start date (YYYY-MM-DD)
- `date_to` (required): End date (YYYY-MM-DD)

**Response:**
```json
[
  {
    "date": "2024-01-01",
    "total_comments": 15,
    "blocked_comments": 2,
    "active_comments": 13
  }
]
```

## AI Features

### Content Moderation

The API automatically moderates content using Google AI:

- **Posts**: Title and content are checked for inappropriate material
- **Comments**: Content is checked before posting
- **Blocking**: Inappropriate content is blocked and replaced with "[Blocked by moderation]"

### Auto-Reply System

When enabled on a post, the system automatically generates replies to comments:

- **Delay**: Configurable delay (default: 60 seconds)
- **Context**: Replies are generated based on post and comment content
- **Marking**: Auto-replies are marked with "[Auto-reply]" prefix

## Error Responses

### Standard Error Format
```json
{
  "error": "Error Type",
  "message": "Detailed error message"
}
```

### Common Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing for production use.

## Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "FastPostAI"
}
``` 