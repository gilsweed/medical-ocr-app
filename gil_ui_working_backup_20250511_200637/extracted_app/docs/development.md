# Development Guide

## Environment Setup

### Prerequisites
1. Node.js (v14 or higher)
2. Python 3.8 or higher
3. Tesseract OCR
4. Git

### Initial Setup
1. Clone the repository
2. Run `./setup.sh` to set up the development environment
3. Review the configuration in `frontend/src/main.js`

## Project Structure

```
Electron/
├── frontend/
│   ├── src/
│   │   ├── main.js         # Electron main process
│   │   └── index.html      # Main application window
│   └── package.json        # Frontend dependencies
├── backend/
│   ├── src/
│   │   └── app.py         # FastAPI backend
│   ├── requirements.txt   # Python dependencies
│   └── venv/             # Python virtual environment
├── docs/
│   ├── api.md            # API documentation
│   ├── development.md    # Development guide
│   └── project_history.md # Project history
├── logs/                 # Application logs
├── setup.sh             # Setup script
├── start.sh            # Start script
├── cleanup.sh         # Cleanup script
└── README.md         # Project overview
```

## Development Workflow

### Starting Development
1. Run `./start.sh` to launch the application in development mode
2. Frontend changes will trigger automatic reload
3. Backend changes require manual restart

### Making Changes

#### Frontend Changes
1. Edit files in `frontend/src/`
2. Changes are automatically reloaded
3. Use Chrome DevTools for debugging (View -> Toggle Developer Tools)

#### Backend Changes
1. Edit files in `backend/src/`
2. Restart the application using `./start.sh`
3. Check logs in `logs/` directory

### Code Style

#### JavaScript/Electron
- Use ES6+ features
- Follow Airbnb JavaScript Style Guide
- Use async/await for asynchronous operations
- Implement proper error handling

#### Python/FastAPI
- Follow PEP 8 style guide
- Use type hints
- Implement proper error handling
- Write docstrings for functions

### Testing

#### Frontend Testing
1. Write tests in `frontend/tests/`
2. Run tests with `npm test`
3. Ensure proper error handling
4. Test edge cases

#### Backend Testing
1. Write tests in `backend/tests/`
2. Run tests with `pytest`
3. Test API endpoints
4. Verify error responses

### Debugging

#### Frontend Debugging
1. Use Chrome DevTools
2. Check console for errors
3. Use debugger statements
4. Monitor IPC communication

#### Backend Debugging
1. Check application logs
2. Use FastAPI's automatic documentation
3. Monitor process status
4. Check port availability

### Building

#### Development Build
```bash
npm run build:dev
```

#### Production Build
```bash
npm run build
```

### Deployment

#### Prerequisites
1. Verify all tests pass
2. Check for security issues
3. Update documentation
4. Review changes

#### Steps
1. Build the application
2. Test the build
3. Create release notes
4. Tag the release
5. Deploy the application

## Best Practices

### Code Organization
- Keep components small and focused
- Use meaningful names
- Implement proper error handling
- Write clear documentation

### Performance
- Optimize image processing
- Implement caching where appropriate
- Monitor memory usage
- Clean up resources

### Security
- Validate input
- Sanitize file paths
- Implement proper error handling
- Use secure dependencies

### Documentation
- Update API documentation
- Document code changes
- Update README
- Maintain change log

## Troubleshooting

### Common Issues

#### Frontend Issues
1. Check Node.js version
2. Verify dependencies
3. Check build errors
4. Review console logs

#### Backend Issues
1. Check Python version
2. Verify virtual environment
3. Check port conflicts
4. Review application logs

### Getting Help
1. Check documentation
2. Review logs
3. Search issues
4. Ask for help

## Contributing

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make changes
4. Write tests
5. Update documentation
6. Submit pull request

### Code Review
1. Review changes
2. Run tests
3. Check style
4. Verify documentation
5. Approve changes

## Resources

### Documentation
- [Electron Documentation](https://www.electronjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tesseract Documentation](https://tesseract-ocr.github.io/)

### Tools
- [Node.js](https://nodejs.org/)
- [Python](https://www.python.org/)
- [Git](https://git-scm.com/)
- [Visual Studio Code](https://code.visualstudio.com/) 