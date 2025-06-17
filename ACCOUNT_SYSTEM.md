# Account System for Toolbox.io

## Overview

A simple but secure account system has been implemented for Toolbox.io with the following features:

- User registration and login
- Secure password hashing with bcrypt
- JWT token-based authentication
- Password change functionality
- SQLite database for user storage

## Architecture

### Backend Components

1. **Database Layer** (`server/database.py`)
   - SQLAlchemy ORM setup
   - SQLite database with User model
   - Automatic table creation

2. **Authentication Utilities** (`server/auth.py`)
   - Password hashing with bcrypt
   - JWT token creation and verification
   - User authentication functions

3. **API Routes** (`server/routes/auth.py`)
   - `/api/auth/register` - User registration
   - `/api/auth/login` - User login
   - `/api/auth/me` - Get current user info
   - `/api/auth/change-password` - Change password
   - `/api/auth/health` - Health check

4. **Data Models** (`server/models.py`)
   - Pydantic models for request/response validation

### Frontend Components

1. **Login Page** (`src/login.html`)
   - Username and password fields
   - Form validation and error handling
   - Automatic redirect to account page on success

2. **Account Page** (`src/account/`)
   - `index.html` - Main account page HTML
   - `style.scss` - Account page styles (compiled to `style.css`)
   - `main.ts` - Account page functionality (compiled to `main.js`)
   - Display user information
   - Password change dialog with confirmation
   - Logout functionality

3. **Registration Page** (`src/register.html`)
   - User registration form
   - Email and password validation

4. **Header Integration** (`src/common.ts`)
   - Dynamic login/account link
   - Authentication state management

## Security Features

- **Password Hashing**: Uses bcrypt with salt for secure password storage
- **JWT Tokens**: Secure token-based authentication with expiration
- **Input Validation**: Pydantic models ensure data validation
- **CORS Protection**: Configured for cross-origin requests
- **SQL Injection Protection**: SQLAlchemy ORM prevents injection attacks

## Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### POST /api/auth/register
Register a new user account.

**Request:**
```json
{
    "username": "string",
    "email": "user@example.com",
    "password": "string"
}
```

**Response:**
```json
{
    "id": 1,
    "username": "string",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00"
}
```

### POST /api/auth/login
Authenticate user and get access token.

**Request:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "access_token": "jwt_token_here",
    "token_type": "bearer"
}
```

### GET /api/auth/me
Get current user information (requires authentication).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "id": 1,
    "username": "string",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00"
}
```

### POST /api/auth/change-password
Change user password (requires authentication).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request:**
```json
{
    "current_password": "string",
    "new_password": "string"
}
```

**Response:**
```json
{
    "message": "Password changed successfully"
}
```

## Setup Instructions

1. **Install Dependencies**
   ```bash
   cd server
   pip install -r requirements.txt
   ```

2. **Initialize Database**
   ```bash
   cd server
   python3 init_db.py
   ```

3. **Build Frontend**
   ```bash
   cd src
   npm install
   npm run build
   ```

4. **Start Server**
   ```bash
   cd server
   python3 main.py
   ```

## Test User

A test user is automatically created during database initialization:

- **Username**: `testuser`
- **Password**: `password123`
- **Email**: `test@example.com`

## Environment Variables

- `SECRET_KEY`: JWT secret key (default: "your-secret-key-change-in-production")

## Security Considerations

1. **Change the SECRET_KEY** in production
2. **Use HTTPS** in production
3. **Implement rate limiting** for login attempts
4. **Add password complexity requirements**
5. **Implement email verification**
6. **Add session management**
7. **Use environment variables** for sensitive configuration

## Future Enhancements

- Email verification system
- Password reset functionality
- Two-factor authentication
- User profile management
- Admin panel
- Audit logging
- Rate limiting
- Session management 