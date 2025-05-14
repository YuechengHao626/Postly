# Postly API Documentation

## Authentication

### Register User
- **URL**: `/api/auth/register/`
- **Method**: `POST`
- **Auth required**: No
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string",
    "email": "string"
  }
  ```
- **Success Response**:
  - **Code**: 201 Created
  - **Content**: `{ "message": "User created successfully" }`
- **Error Response**:
  - **Code**: 400 Bad Request
  - **Content**: `{ "field": ["error message"] }`

### Login User
- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Auth required**: No
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: 
    ```json
    {
      "access": "string",    // JWT access token, 用于API认证
      "refresh": "string",   // JWT refresh token, 用于刷新access token和登出
      "role": "string"       // 用户角色
    }
    ```
- **Error Response**:
  - **Code**: 401 Unauthorized
  - **Content**: `{ "error": "Invalid credentials" }`
  - **Code**: 400 Bad Request
  - **Content**: `{ "field": ["error message"] }`

### Logout User
- **URL**: `/api/auth/logout/`
- **Method**: `POST`
- **Auth required**: Yes (需要在请求头中包含有效的access token)
- **Request Headers**:
  ```
  Authorization: Bearer <access_token>
  ```
- **Request Body**:
  ```json
  {
    "refresh_token": "string"  // 登录时获取的refresh token
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: `{ "message": "Successfully logged out" }`
- **Error Response**:
  - **Code**: 401 Unauthorized
  - **Content**: `{ "error": "Token is invalid or has been blacklisted" }`
  - **Code**: 400 Bad Request
  - **Content**: `{ "error": "Refresh token is required" }`

### Token Usage
- Access Token 用于API认证，需要在请求头中添加：
  ```
  Authorization: Bearer <access_token>
  ```
- Access Token 和 Refresh Token 有效期均为7天
- Refresh Token 用于：
  1. 登出时将token加入黑名单
  2. 在Access Token过期后获取新的Access Token
- 登出后的token会被加入黑名单，无法再次使用
- 所有需要认证的API都需要在请求头中携带有效的Access Token
- 使用已登出（黑名单中）的token访问API会返回401状态码

## Posts

### List Posts
- **URL**: `/api/posts/`
- **Method**: `GET`
- **Auth required**: No
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Array of post objects

### Create Post
- **URL**: `/api/posts/`
- **Method**: `POST`
- **Auth required**: Yes
- **Request Body**:
  ```json
  {
    "title": "string",
    "content": "string",
    "subforum_id": "integer"
  }
  ```
- **Success Response**:
  - **Code**: 201 Created
  - **Content**: Post object
- **Error Response**:
  - **Code**: 400 Bad Request
  - **Content**: `{ "detail": "error message" }`
  - **Code**: 403 Forbidden
  - **Content**: `{ "detail": "You are banned from posting" }`

### Get Post Comments
- **URL**: `/api/posts/{post_id}/comments/`
- **Method**: `GET`
- **Auth required**: No
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Array of comment objects

## Comments

### List Comments
- **URL**: `/api/comments/`
- **Method**: `GET`
- **Auth required**: No
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Array of comment objects

### Create Comment
- **URL**: `/api/comments/`
- **Method**: `POST`
- **Auth required**: Yes
- **Request Body**:
  ```json
  {
    "post_id": "integer",
    "content": "string",
    "reply_to_user_id": "integer" // optional
  }
  ```
- **Success Response**:
  - **Code**: 201 Created
  - **Content**: Comment object
- **Error Response**:
  - **Code**: 400 Bad Request
  - **Content**: `{ "detail": "error message" }`
  - **Code**: 403 Forbidden
  - **Content**: `{ "detail": "You are banned from posting" }`

## Voting

### Create Vote
- **URL**: `/api/votes/`
- **Method**: `POST`
- **Auth required**: Yes
- **Request Body**:
  ```json
  {
    "target_type": "post" | "comment",
    "target_id": "integer"
  }
  ```
- **Success Response**:
  - **Code**: 201 Created
  - **Content**: Vote object
- **Error Response**:
  - **Code**: 400 Bad Request
  - **Content**: `{ "detail": "Target does not exist" }`

## Forums

### List SubForums
- **URL**: `/api/forums/`
- **Method**: `GET`
- **Auth required**: No
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Array of subforum objects

### Create SubForum
- **URL**: `/api/forums/`
- **Method**: `POST`
- **Auth required**: Yes
- **Request Body**:
  ```json
  {
    "name": "string",
    "description": "string"
  }
  ```
- **Success Response**:
  - **Code**: 201 Created
  - **Content**: Subforum object

### Get SubForum Posts
- **URL**: `/api/forums/{forum_id}/posts/`
- **Method**: `GET`
- **Auth required**: No
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Array of post objects

## Search

### Search Posts
- **URL**: `/api/search/posts/`
- **Method**: `GET`
- **Auth required**: No
- **Query Parameters**:
  - `q`: Search query (required)
  - `page`: Page number (default: 1)
  - `page_size`: Items per page (default: 10)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: 
    ```json
    {
      "total": "integer",
      "page": "integer",
      "page_size": "integer",
      "results": []
    }
    ```
- **Error Response**:
  - **Code**: 400 Bad Request
  - **Content**: `{ "error": "Search query is required" }`

### Search SubForums
- **URL**: `/api/search/subforums/`
- **Method**: `GET`
- **Auth required**: No
- **Query Parameters**:
  - `q`: Search query (required)
  - `page`: Page number (default: 1)
  - `page_size`: Items per page (default: 10)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: 
    ```json
    {
      "total": "integer",
      "page": "integer",
      "page_size": "integer",
      "results": []
    }
    ```
- **Error Response**:
  - **Code**: 400 Bad Request
  - **Content**: `{ "error": "Search query is required" }`

### Search Users
- **URL**: `/api/search/users/`
- **Method**: `GET`
- **Auth required**: No
- **Query Parameters**:
  - `q`: Search query (required)
  - `page`: Page number (default: 1)
  - `page_size`: Items per page (default: 10, max: 100)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Paginated list of user objects

## Moderation

### Assign Moderator
- **URL**: `/api/moderator/{subforum_id}/assign/`
- **Method**: `POST`
- **Auth required**: Yes (Super Admin or SubForum Admin)
- **Request Body**:
  ```json
  {
    "user_id": "integer"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: `{ "detail": "Moderator assigned successfully" }`
- **Error Response**:
  - **Code**: 403 Forbidden
  - **Content**: `{ "detail": "You don't have permission to assign moderators" }`

### Assign SubForum Admin
- **URL**: `/api/moderator/{subforum_id}/assign-admin/`
- **Method**: `POST`
- **Auth required**: Yes (Super Admin only)
- **Request Body**:
  ```json
  {
    "user_id": "integer"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: `{ "detail": "Subforum admin assigned successfully" }`
- **Error Response**:
  - **Code**: 403 Forbidden
  - **Content**: `{ "detail": "Only super admin can assign subforum admins" }`

### Remove Moderator
- **URL**: `/api/moderator/{subforum_id}/remove/`
- **Method**: `POST`
- **Auth required**: Yes (Super Admin or SubForum Admin)
- **Request Body**:
  ```json
  {
    "user_id": "integer"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: `{ "detail": "Moderator removed successfully" }`
- **Error Response**:
  - **Code**: 403 Forbidden
  - **Content**: `{ "detail": "You don't have permission to remove moderators" }`

## Ban Management

### Global Ban User
- **URL**: `/api/ban/global/`
- **Method**: `POST`
- **Auth required**: Yes (Super Admin only)
- **Request Body**:
  ```json
  {
    "user_id": "integer",
    "action": "ban" | "unban",
    "reason": "string" // optional
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: `{ "detail": "User has been banned/unbanned successfully" }`
- **Error Response**:
  - **Code**: 403 Forbidden
  - **Content**: `{ "detail": "Only super admins can perform global bans" }`

### SubForum Ban User
- **URL**: `/api/ban/subforum/`
- **Method**: `POST`
- **Auth required**: Yes (Super Admin or SubForum Admin)
- **Request Body**:
  ```json
  {
    "user_id": "integer",
    "subforum_id": "integer",
    "duration_days": "integer",
    "reason": "string" // optional
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Ban record object
- **Error Response**:
  - **Code**: 403 Forbidden
  - **Content**: `{ "detail": "You don't have permission to ban users in this subforum" }`

### SubForum Unban User
- **URL**: `/api/ban/subforum/unban/`
- **Method**: `POST`
- **Auth required**: Yes (Super Admin or SubForum Admin)
- **Request Body**:
  ```json
  {
    "user_id": "integer",
    "subforum_id": "integer"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: `{ "detail": "User has been unbanned from the subforum successfully" }`
- **Error Response**:
  - **Code**: 403 Forbidden
  - **Content**: `{ "detail": "You don't have permission to unban users in this subforum" }` 