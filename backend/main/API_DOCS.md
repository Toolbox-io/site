# Toolbox.io API Documentation

## Base URL
- **Production:** `https://toolbox-io.ru`
- **Beta:** `https://beta.toolbox-io.ru`
- **Local:** `http://localhost:8000`

---

## Authentication & Account Endpoints

All `/api/auth/*` endpoints are under the `/api/auth` prefix.

### POST `/api/auth/register`
- **Description:** Register a new user.
- **Request Body:**
  ```json
  {
    "username": "<string>",
    "email": "<string>",
    "password": "<string>"
  }
  ```
- **Response:**
  `200 OK`
  ```json
  {
    "id": 1,
    "username": "<string>",
    "email": "<string>",
    "created_at": "<date>T<time>Z"
  }
  ```
- **Errors:**
  - `400`: Username/email already registered, weak password, etc.

---

### POST `/api/auth/login`
- **Description:** Log in and receive a JWT token.
- **Request Body:**
  ```json
  {
    "username": "<string>",
    "password": "<string>"
  }
  ```
- **Response:**
  `200 OK`
  ```json
  {
    "access_token": "<jwt_token>"
  }
  ```
- **Errors:**
  - `401`: Incorrect credentials, email not verified.

---

### POST `/api/auth/logout`
- **Description:** Log out and blacklist the current token.
- **Headers:**
  `Authorization: Bearer <access_token>`
- **Response:**
  ```json
  { "message": "Logged out successfully" }
  ```

---

### GET `/api/auth/check-auth`
- **Description:** Check if the current token is valid.
- **Headers:**
  `Authorization: Bearer <access_token>`
- **Response:**
  ```json
  { "authenticated": true, "user": "<username>" }
  ```

---

### GET `/api/auth/user-info`
- **Description:** Get info about the current user.
- **Headers:**
  `Authorization: Bearer <access_token>`
- **Response:**
  ```json
  {
    "id": 1,
    "username": "<string>",
    "email": "<string>",
    "created_at": "<date>T<time>Z"
  }
  ```

---

### POST `/api/auth/request-reset`
- **Description:** Request a password reset email.
- **Request Body:**
  ```json
  { "email": "<string>" }
  ```
- **Response:**
  ```json
  { "success": true }
  ```

---

### POST `/api/auth/reset-password`
- **Description:** Reset password using a token.
- **Request Body:**
  ```json
  {
    "token": "<reset_token>",
    "new_password": "<string>"
  }
  ```
- **Response:**
  ```json
  { "success": true }
  ```

---

### POST `/api/auth/verify-email`
- **Description:** Request a verification email.
- **Request Body:**
  ```json
  { "email": "<string>" }
  ```
- **Response:**
  ```json
  { "success": true }
  ```

---

### GET/POST `/api/auth/verify`
- **Description:** Verify email using a token (from email link).
- **Query Parameter:**
  `?token=...`
- **Response:**

  If method is `POST`: `{"success": true}` on success.
  
  If method is `GET`: Redirects to `/account/login?verified=true` on success.

---

### POST `/api/auth/change-password`
- **Description:** Change the current user's password.
- **Headers:**
  `Authorization: Bearer <access_token>`
- **Request Body:**
  ```json
  {
    "current_password": "<string>",
    "new_password": "<string>"
  }
  ```
- **Response:**
  ```json
  { "message": "Password changed successfully" }
  ```

---

### DELETE `/api/auth/delete-account`
- **Description:** Delete the current user's account.
- **Headers:**
  `Authorization: Bearer <access_token>`
- **Response:**
  ```json
  { "message": "Account deleted successfully" }
  ```

---

## Guides Endpoints

### GET `/guides/list`
- **Description:** List all available guides.
- **Response:**
  ```json
  [
    {
      "name": "HOW_TO_INSTALL.md",
      "header": { 
        "title": "How to Install",
        "icon": "download"
      }
    },
    // ...
  ]
  ```

### GET `/guides/list/{guide}`
- **Description:** Get metadata for a specific guide.
- **Response:**
  ```json
  { 
    "title": "How to Install",
    "icon": "download"
  }
  ```

### GET `/guides/{guide}/raw`
- **Description:** Get the raw HTML template for a guide.

---

## Error Handling

- 404: Not found (returns a custom error page if available)
- 401/403: Unauthorized/Forbidden (returns a custom error page if available)
- 400: Bad request (invalid input, etc.)

---

## Authentication

- All protected endpoints require the `Authorization: Bearer <access_token>` header.
- JWT tokens are returned by `/api/auth/login` and must be stored securely on the client.

---

## Photo Storage Endpoints

All `/photos/*` endpoints are under the `/photos` prefix and require authentication (`Authorization: Bearer <access_token>`).

### GET `/photos/sync`
- **Description:** List all photo UUIDs and metadata for the authenticated user (for sync).
- **Headers:**
  - `Authorization: Bearer <access_token>`
- **Response:**
  ```json
  {
    "photos": [
      {"uuid": "<uuid>", "uploaded_at": "<date>T<time>Z", "filename": "<string>"}
      // ...
    ]
  }
  ```
- **Errors:**
  - `401`: Unauthorized (invalid or missing token)

---

### POST `/photos/upload`
- **Description:** Upload an encrypted photo file with a client-generated UUID.
- **Headers:**
  - `Authorization: Bearer <access_token>`
- **Request (multipart/form-data):**
  - `photo_uuid`: string (UUID, required)
  - `file`: binary (encrypted photo, required)
- **Response:**
  `201 Created`
  ```json
  { "status": "success" }
  ```
- **Errors:**
  - `400`: Photo UUID already exists for this user
  - `401`: Unauthorized (invalid or missing token)

---

### GET `/photos/download/{photo_uuid}`
- **Description:** Download the encrypted photo file for the given UUID (if it belongs to the user).
- **Headers:**
  - `Authorization: Bearer <access_token>`
- **Response:**
  - Content-Type: `application/octet-stream`
  - File download (binary)
- **Errors:**
  - `404`: Photo not found or file missing
  - `401`: Unauthorized (invalid or missing token)