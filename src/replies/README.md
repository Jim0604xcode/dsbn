# Replies Module Implementation

## Overview
This module implements the reply functionality for the DeepSoul backend application, allowing users to create replies to shared posts (Life Moments, Life Trajectories, and Messages to You).

## Files Created

### 1. `models.py`
- **RepliesMaster**: SQLAlchemy model for the replies_master table
- Includes proper relationships with PostMaster and User models
- Uses TimestampMixin for created_at and updated_at fields
- Supports nested replies through parent_reply_master_id

### 2. `schemas.py`
- **CreateReplyRequest**: Pydantic schema for reply creation requests
- **ReplyResponse**: Pydantic schema for reply responses
- Includes validation for content length and optional parent reply ID

### 3. `service.py`
- **create_reply()**: Core function implementing the business logic
  - Validates user permissions to reply to the post
  - Checks if parent reply exists and belongs to the same post
  - Creates new reply in the database
  - Sends push notifications to relevant users
  - Returns the created reply object
- **delete_reply()**: Soft delete replies by marking as deleted
- **edit_reply()**: Edit reply content with permission validation
- **get_replies_only()**: Retrieve replies with user info and filtering
- **_send_push_by_create_reply()**: Internal push notification function

### 4. `router.py`
- **Create Reply Endpoints**:
  - `POST /replies/life_moment/{id}`
  - `POST /replies/life_trajectory/{id}`
  - `POST /replies/message_to_you/{id}`
- **Management Endpoints**:
  - `DELETE /replies/{reply_master_id}`
  - `PUT /replies/{reply_master_id}`
- **Retrieval Endpoints**:
  - `GET /replies/life_moment/{id}`
  - `GET /replies/life_trajectory/{id}`
  - `GET /replies/message_to_you/{id}`

### 5. `validators.py`
- Content validation functions
- Reply ID validation functions
- Following existing project validation patterns

### 6. `constants.py`
- **REPLY_NOTIFICATION_MESSAGES**: Localized push notification messages
  - English, Simplified Chinese, Traditional Chinese
  - Different messages for replies to posts vs replies to comments

### 7. `utils.py`
- Helper functions for permission checking
- Parent reply validation utilities
- Reusable utility functions

## API Endpoints

### Create Reply Endpoints
```
POST /replies/life_moment/{id}
POST /replies/life_trajectory/{id}
POST /replies/message_to_you/{id}
```
**Parameters:**
- `id` (path): The shared_post_id
- `content` (body): The reply content
- `parent_reply_master_id` (body, optional): Parent reply ID for nested replies

### Management Endpoints
```
DELETE /replies/{reply_master_id}  # Soft delete reply
PUT /replies/{reply_master_id}     # Edit reply content
```

### Retrieval Endpoints
```
GET /replies/life_moment/{id}      # Get replies for life moment
GET /replies/life_trajectory/{id}  # Get replies for life trajectory
GET /replies/message_to_you/{id}   # Get replies for message to you
```

## Core Functions

### create_reply()
```python
def create_reply(post_source: PostSourceEnum, shared_post_id: int, user_id: str, 
                content: str, parent_reply_master_id: int = None, db: Session = None)
```
**Functionality:**
1. Permission validation (post owner or shared recipient)
2. Parent reply validation (if nested reply)
3. Reply creation in database
4. Push notification sending

### get_replies_only()
```python
async def get_replies_only(post_source: PostSourceEnum, shared_post_id: int, 
                          user_id: str, db: Session)
```
**Functionality:**
1. Permission-based reply filtering
2. Deleted reply chain preservation
3. User info enrichment
4. Hierarchical reply structure

### Database Schema Integration
The implementation works with the existing `replies_master` table schema:
- `id`: Primary key
- `post_master_id`: References the original post
- `user_id`: The user creating the reply
- `parent_reply_master_id`: For nested replies (NULL for direct replies)
- `content`: The reply text
- `is_deleted`: Soft delete flag
- `created_at`, `updated_at`: Timestamps

## Integration Points

### 1. Main Application
- Added replies router to `main.py`
- Imported RepliesMaster model for SQLAlchemy registration

### 2. Posts Module
- Added replies relationship to PostMaster model
- Integrated with existing permission system

### 3. Database Relationships
- RepliesMaster → PostMaster (many-to-one)
- RepliesMaster → User (many-to-one)
- RepliesMaster → RepliesMaster (self-referencing for nested replies)

## Testing
- **Unit Tests**: `tests/test_reply_push_notification.py`
  - Tests push notification functionality
  - Mocks external dependencies
  - Covers edge cases and error scenarios
- **API Tests**: `tests/test_create_reply_api.py`
  - Tests all reply endpoints
  - Includes nested reply testing
  - Permission validation tests

**Run Tests:**
```bash
python -m pytest tests/test_reply_push_notification.py -v
python -m pytest tests/test_create_reply_api.py -v
```

## Security & Permissions
- Uses existing JWT authentication
- Validates user permissions through post sharing system
- Prevents unauthorized replies to non-shared posts
- Validates parent reply ownership

## Error Handling
- Follows existing project error handling patterns
- Returns appropriate HTTP status codes
- Provides descriptive error messages
- Uses existing BadReqExpection for validation errors

## Push Notifications
- **Localized Messages**: Support for English, Chinese (Simplified & Traditional)
- **Smart Targeting**: Notifies post owners and parent reply authors
- **Payload Data**: Includes reply and post context for client handling
- **Error Handling**: Non-blocking - reply creation succeeds even if notification fails

## Features Implemented
✅ **Core Reply System**
- Create, edit, delete replies
- Nested reply support
- Permission-based access control

✅ **Push Notifications**
- Multi-language support
- Smart recipient targeting
- Rich payload data

✅ **Reply Management**
- Soft delete with content clearing
- Reply chain preservation
- Visibility filtering for non-owners

✅ **Testing Coverage**
- Unit tests for push notifications
- API endpoint testing
- Mock-based isolated testing