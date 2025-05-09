import React, { useState, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  AppBar,
  Toolbar,
  IconButton,
  CircularProgress,
  Button,
  Snackbar,
  Alert,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Switch,
  FormControlLabel,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  Menu as MenuIcon,
  Settings as SettingsIcon,
  ContentCopy as CopyIcon,
  Refresh as RefreshIcon,
  Image as ImageIcon,
  Description as DescriptionIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import './App.css';

function App() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [preview, setPreview] = useState(null);
  const [settings, setSettings] = useState({
    language: 'eng',
    dpi: 300,
    enhanceImage: true,
    autoRotate: true
  });

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    setLoading(true);
    setError(null);

    try {
      const file = acceptedFiles[0];
      
      // Create preview for images
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = () => setPreview(reader.result);
        reader.readAsDataURL(file);
      } else {
        setPreview(null);
      }

      const result = await window.electron.processImage(file.path);
      
      if (result.success) {
        setText(result.text);
        setSnackbar({
          open: true,
          message: 'File processed successfully',
          severity: 'success'
        });
      } else {
        setError(result.error || 'Failed to process file');
        setSnackbar({
          open: true,
          message: result.error || 'Failed to process file',
          severity: 'error'
        });
      }
    } catch (err) {
      setError(err.message);
      setSnackbar({
        open: true,
        message: err.message,
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg'],
      'application/pdf': ['.pdf']
    }
  });

  const handleCopyText = () => {
    navigator.clipboard.writeText(text);
    setSnackbar({
      open: true,
      message: 'Text copied to clipboard',
      severity: 'success'
    });
  };

  const handleRetry = () => {
    setError(null);
    setText('');
    setPreview(null);
  };

  const handleSettingsChange = (setting, value) => {
    setSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => setDrawerOpen(true)}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            OCR Scanner
          </Typography>
          <IconButton color="inherit" onClick={() => setDrawerOpen(true)}>
            <SettingsIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ flexGrow: 1, py: 4 }}>
        <Paper
          {...getRootProps()}
          sx={{
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            bgcolor: isDragActive ? 'action.hover' : 'background.paper',
            border: '2px dashed',
            borderColor: isDragActive ? 'primary.main' : 'divider',
            mb: 3
          }}
        >
          <input {...getInputProps()} />
          {preview ? (
            <Box sx={{ mb: 2 }}>
              <img
                src={preview}
                alt="Preview"
                style={{ maxWidth: '100%', maxHeight: '200px', objectFit: 'contain' }}
              />
            </Box>
          ) : (
            <Box sx={{ py: 4 }}>
              <ImageIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {isDragActive
                  ? 'Drop the file here'
                  : 'Drag and drop a file here, or click to select'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Supports PNG, JPG, JPEG, and PDF files
              </Typography>
            </Box>
          )}
        </Paper>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Paper sx={{ p: 2, mb: 3, bgcolor: 'error.light' }}>
            <Typography color="error" gutterBottom>
              {error}
            </Typography>
            <Button
              startIcon={<RefreshIcon />}
              onClick={handleRetry}
              variant="contained"
              color="error"
            >
              Retry
            </Button>
          </Paper>
        )}

        {text && (
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">Extracted Text</Typography>
              <Button
                startIcon={<CopyIcon />}
                onClick={handleCopyText}
                variant="outlined"
                size="small"
              >
                Copy
              </Button>
            </Box>
            <Typography
              component="pre"
              sx={{
                whiteSpace: 'pre-wrap',
                maxHeight: '400px',
                overflow: 'auto',
                p: 2,
                bgcolor: 'grey.50',
                borderRadius: 1
              }}
            >
              {text}
            </Typography>
          </Paper>
        )}
      </Container>

      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Box sx={{ width: 300, p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">Settings</Typography>
            <IconButton onClick={() => setDrawerOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
          <Divider sx={{ mb: 2 }} />
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Language</InputLabel>
            <Select
              value={settings.language}
              onChange={(e) => handleSettingsChange('language', e.target.value)}
              label="Language"
            >
              <MenuItem value="eng">English</MenuItem>
              <MenuItem value="heb">Hebrew</MenuItem>
              <MenuItem value="ara">Arabic</MenuItem>
            </Select>
          </FormControl>

          <TextField
            fullWidth
            type="number"
            label="DPI"
            value={settings.dpi}
            onChange={(e) => handleSettingsChange('dpi', e.target.value)}
            sx={{ mb: 2 }}
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.enhanceImage}
                onChange={(e) => handleSettingsChange('enhanceImage', e.target.checked)}
              />
            }
            label="Enhance Image"
            sx={{ mb: 1 }}
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.autoRotate}
                onChange={(e) => handleSettingsChange('autoRotate', e.target.checked)}
              />
            }
            label="Auto Rotate"
          />
        </Box>
      </Drawer>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default App; 