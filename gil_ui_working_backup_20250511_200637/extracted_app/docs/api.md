# API Documentation

## Overview
The OCR Scanner application provides a RESTful API for text extraction from images and PDF files. The API is built using FastAPI and runs on port 8080 by default.

## Endpoints

### Health Check
```
GET /health
```

Checks if the API is running and healthy.

#### Response
```json
{
    "status": "healthy"
}
```

### Process Document
```
POST /api/process
```

Processes an image or PDF file and extracts text using OCR.

#### Request Body
```json
{
    "filePath": "string"  // Absolute path to the file
}
```

#### Response
```json
{
    "success": "boolean",
    "text": "string",     // Extracted text (if successful)
    "error": "string"     // Error message (if failed)
}
```

#### Supported File Types
- Images: JPG, JPEG, PNG
- Documents: PDF

## Error Handling

### Common Error Codes
- `400`: Invalid request (unsupported file format)
- `404`: File not found
- `500`: Internal server error

### Error Response Format
```json
{
    "success": false,
    "error": "Error message"
}
```

## Implementation Details

### OCR Processing
- Images are processed using Tesseract OCR
- PDFs are processed using PyMuPDF for text extraction
- Text is cleaned and normalized before being returned

### Performance
- Asynchronous request handling
- Efficient memory management
- Automatic process cleanup

## Security
- CORS enabled for local development
- File access restricted to local system
- Process isolation between requests

## Rate Limiting
- No rate limiting implemented in development
- Consider implementing rate limiting in production

## Logging
- Request logging enabled
- Error logging with stack traces
- Log rotation implemented

## Development Guidelines

### Running the API
1. Ensure Python environment is activated
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `python src/app.py`

### Testing
- Use the health check endpoint to verify the API is running
- Test with various file formats and sizes
- Monitor memory usage during processing

### Debugging
- Check logs in the `logs` directory
- Use FastAPI's automatic documentation at `/docs`
- Monitor process status and port usage

## Production Considerations

### Security
- Implement proper authentication
- Restrict CORS to specific origins
- Add rate limiting
- Implement file size limits

### Performance
- Configure process pool for parallel processing
- Implement caching if needed
- Monitor memory usage
- Set up proper logging

### Deployment
- Use proper process management
- Set up monitoring
- Configure backup systems
- Implement proper error reporting 