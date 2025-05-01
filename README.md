# Vimeo Integration System

A Django-based video management system that integrates with Vimeo for video hosting and processing. The system provides a user-friendly interface for uploading, managing, and viewing videos with real-time processing status updates.

## System Architecture

```mermaid
graph TD
    A[Web Interface] -->|Upload Video| B[Django Backend]
    B -->|Store Video Info| C[(Database)]
    B -->|Upload Video| D[Vimeo API]
    D -->|Processing Status| B
    D -->|Thumbnails| B
    B -->|Status Updates| A
    B -->|Video Player| A
```

## Database Schema

```mermaid
erDiagram
    Video {
        int id PK
        string title
        string description
        string vimeo_id
        datetime upload_date
        string thumbnail_url
        string video_url
        string status
    }
```

## API Endpoints

### Video Management
- `GET /` - Video dashboard
- `GET /upload/` - Upload form
- `POST /upload/` - Handle video upload
- `GET /video/<id>/` - Video player page
- `POST /delete-video/<id>/` - Delete video
- `GET /check-video-status/<vimeo_id>/` - Check processing status
- `GET /check-progress/<vimeo_id>/` - Check upload progress

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd vimeo-integration
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your Vimeo API credentials:
```env
VIMEO_ACCESS_TOKEN=your_access_token
VIMEO_CLIENT_ID=your_client_id
VIMEO_CLIENT_SECRET=your_client_secret
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

## Features

### Video Upload
- Support for large video files (up to 500MB)
- Progress tracking during upload
- Automatic thumbnail generation
- Processing status monitoring

### Video Management
- Video listing with thumbnails
- Processing status indicators
- Delete functionality
- Video player integration

### Technical Features
- CORS support for cross-origin requests (ngrok compatibility)
- Chunked file uploads
- Real-time status updates
- Error handling and validation

## System Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant V as Vimeo API
    participant D as Database

    U->>F: Select video file
    F->>B: Upload video
    B->>V: Create video container
    V-->>B: Return upload URL
    B->>V: Upload video chunks
    B->>D: Create video record
    V-->>B: Processing status
    B-->>F: Update status
    F-->>U: Show progress
    
    loop Status Check
        F->>B: Check status
        B->>V: Get video status
        V-->>B: Return status
        B-->>F: Update UI
    end
```

## Security Considerations

- CSRF protection for form submissions
- Secure file handling
- API key management through environment variables
- Input validation and sanitization
- Cross-origin resource sharing (CORS) configuration

## Error Handling

The system includes comprehensive error handling for:
- File size validation
- Upload failures
- Processing errors
- API communication issues
- Database operations

## Development with ngrok

To use the system with ngrok:
1. Install ngrok
2. Run: `ngrok http 8000`
3. Use the provided URL to access the system

The system includes CORS headers and CSRF exemptions to work seamlessly with ngrok tunneling.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Vimeo API for video hosting
- Django framework
- Bootstrap for UI components 