# Chat System Documentation

## Overview

This chat system provides real-time communication between users and administrators in the educational platform. It replaces the traditional "Contact Us" form with an interactive chat interface.

## Features

### ✅ Implemented Features
- **1-on-1 Chat**: Each user has a private conversation with admin
- **Real-time Updates**: Polling-based message updates (every 3 seconds)
- **Message Management**: Send, receive, and mark messages as read
- **Unread Count**: Track unread messages for both users and admins
- **Admin Interface**: Admins can view all conversations and reply to any user
- **User Interface**: Users can chat with admin through the support chat
- **Message History**: Paginated message history with date grouping
- **Responsive Design**: Mobile-friendly chat interface

### 🚀 Future Enhancements
- **WebSocket Support**: Real-time messaging without polling
- **File Attachments**: Send images and documents
- **Message Status**: Typing indicators and delivery confirmations
- **Push Notifications**: Browser notifications for new messages
- **Chat Analytics**: Message statistics and response times
- **Auto-responses**: Bot responses for common queries

## Architecture

### Backend (Django REST Framework)

#### Models
- **Conversation**: Links a user with admin, tracks conversation metadata
- **Message**: Individual messages with sender, content, read status
- **MessageReadStatus**: Future enhancement for group chat read tracking

#### API Endpoints
```
GET  /api/chat/conversation/                    # Get/create user's conversation
POST /api/chat/conversation/                    # Create new conversation
GET  /api/chat/conversations/                   # List all conversations (admin)
GET  /api/chat/conversations/{id}/              # Get conversation details
GET  /api/chat/conversations/{id}/messages/     # Get messages (paginated)
POST /api/chat/conversations/{id}/messages/     # Send message
POST /api/chat/messages/mark-read/              # Mark specific messages as read
POST /api/chat/conversations/{id}/mark-read/    # Mark conversation as read
GET  /api/chat/unread-count/                    # Get unread message count
GET  /api/chat/conversations/{id}/unread-count/ # Get conversation unread count
```

#### Security
- JWT authentication required for all endpoints
- Users can only access their own conversations
- Admins can access all conversations
- Proper permission checks for message sending

### Frontend (React + Vite)

#### Components
- **ChatInterface**: Main chat UI for users
- **AdminChatInterface**: Admin interface with conversation list
- **ChatNotificationBell**: Unread message indicator

#### Features
- **Polling**: Automatic message updates every 3 seconds
- **Auto-scroll**: Messages automatically scroll to bottom
- **Date Grouping**: Messages grouped by date for better UX
- **Read Status**: Visual indicators for message read status
- **Error Handling**: User-friendly error messages
- **Loading States**: Loading indicators for better UX

## Installation & Setup

### Backend Setup
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**:
   ```bash
   python manage.py makemigrations chat
   python manage.py migrate
   ```

3. **Start Server**:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup
1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm run dev
   ```

## Usage

### For Users
1. Navigate to `/contact` page
2. The chat interface will automatically load your conversation
3. Type messages and click send
4. Messages update automatically every 3 seconds

### For Admins
1. Navigate to `/admin/chat` or use the sidebar in admin dashboard
2. View all user conversations in the sidebar
3. Click on a conversation to view messages
4. Reply to users directly from the interface

## Database Schema

### Conversation Table
```sql
CREATE TABLE chat_conversations (
    id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES auth_user(id),
    created_at TIMESTAMP,
    last_message_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Message Table
```sql
CREATE TABLE chat_messages (
    id BIGINT PRIMARY KEY,
    conversation_id BIGINT REFERENCES chat_conversations(id),
    sender_id BIGINT REFERENCES auth_user(id),
    content TEXT,
    message_type VARCHAR(10) DEFAULT 'text',
    attachment VARCHAR(255),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);
```

## API Examples

### Send a Message
```javascript
const response = await fetch('/api/chat/conversations/1/messages/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-jwt-token',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    content: 'Hello, I need help with my course',
    message_type: 'text'
  })
});
```

### Get Messages
```javascript
const response = await fetch('/api/chat/conversations/1/messages/', {
  headers: {
    'Authorization': 'Bearer your-jwt-token'
  }
});
const data = await response.json();
```

### Mark Messages as Read
```javascript
const response = await fetch('/api/chat/conversations/1/mark-read/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-jwt-token'
  }
});
```

## Configuration

### Polling Interval
Update the polling interval in the frontend components:
```javascript
// In ChatInterface.jsx and AdminChatInterface.jsx
pollIntervalRef.current = setInterval(pollForMessages, 3000); // 3 seconds
```

### Message Pagination
Configure message pagination in backend:
```python
# In chat/views.py
class MessagePagination(PageNumberPagination):
    page_size = 20  # Messages per page
    max_page_size = 100
```

## Testing

### Backend Testing
Run the test script to verify API endpoints:
```bash
python test_chat_api.py
```

### Manual Testing
1. Create a user account
2. Login as user and visit `/contact`
3. Send a test message
4. Login as admin and visit `/admin/chat`
5. Verify the message appears and reply

## Troubleshooting

### Common Issues

1. **Messages not loading**:
   - Check JWT token is valid
   - Verify user has a conversation
   - Check browser console for errors

2. **Polling not working**:
   - Check network connectivity
   - Verify API endpoints are accessible
   - Check for CORS issues

3. **Admin can't see conversations**:
   - Verify user has admin role
   - Check conversation permissions
   - Ensure conversations exist

### Debug Mode
Enable debug logging in Django settings:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'chat': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Performance Considerations

### Database Optimization
- Messages are indexed by conversation and timestamp
- Pagination prevents loading too many messages
- Read status queries are optimized

### Frontend Optimization
- Polling interval is configurable
- Messages are cached in component state
- Auto-scroll is debounced

### Future Optimizations
- Implement WebSocket for real-time updates
- Add Redis caching for message counts
- Implement message compression for large conversations

## Security Considerations

### Authentication
- All endpoints require JWT authentication
- Token expiration is handled gracefully
- Session management follows best practices

### Authorization
- Users can only access their own conversations
- Admins can access all conversations
- Message sending permissions are enforced

### Data Protection
- Messages are stored securely in database
- No sensitive data in URLs
- Proper error handling prevents information leakage

## Contributing

When adding new features:
1. Update models and run migrations
2. Add API endpoints with proper permissions
3. Update frontend components
4. Add tests for new functionality
5. Update documentation

## License

This chat system is part of the educational platform project.
