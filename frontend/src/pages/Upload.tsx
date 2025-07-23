import React, { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Chip,
  Alert,
  LinearProgress,
  Grid,
} from '@mui/material';
import {
  CloudUpload,
  AttachFile,
  Add,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';

const Upload: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [xmlFile, setXmlFile] = useState<File | null>(null);
  const [tags, setTags] = useState<string[]>([]);
  const [currentTag, setCurrentTag] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/*': ['.txt'],
      'image/*': ['.png', '.jpg', '.jpeg', '.gif'],
    },
  });

  const handleXmlFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'text/xml') {
      setXmlFile(file);
    }
  };

  const handleAddTag = () => {
    if (currentTag.trim() && !tags.includes(currentTag.trim())) {
      setTags([...tags, currentTag.trim()]);
      setCurrentTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadProgress(0);

    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setUploading(false);
          return 100;
        }
        return prev + 10;
      });
    }, 200);

    // TODO: Implement actual file upload to backend
    console.log('Uploading file:', selectedFile);
    console.log('XML metadata file:', xmlFile);
    console.log('Tags:', tags);
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Upload Files
      </Typography>

      <Grid container spacing={3}>
        {/* File Upload */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Select File
            </Typography>
            
            <Box
              {...getRootProps()}
              sx={{
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'grey.300',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
                mb: 3,
              }}
            >
              <input {...getInputProps()} />
              <CloudUpload sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {isDragActive
                  ? 'Drop the file here'
                  : 'Drag & drop a file here, or click to select'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Supports PDF, Word, Excel, images, and text files
              </Typography>
            </Box>

            {selectedFile && (
              <Alert severity="success" sx={{ mb: 3 }}>
                Selected file: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
              </Alert>
            )}

            {/* XML Metadata File */}
            <Typography variant="h6" gutterBottom>
              XML Metadata (Optional)
            </Typography>
            <Button
              variant="outlined"
              component="label"
              startIcon={<AttachFile />}
              sx={{ mb: 3 }}
            >
              Choose XML File
              <input
                type="file"
                accept=".xml"
                onChange={handleXmlFileChange}
                hidden
              />
            </Button>

            {xmlFile && (
              <Alert severity="info" sx={{ mb: 3 }}>
                XML file: {xmlFile.name}
              </Alert>
            )}

            {/* Tags */}
            <Typography variant="h6" gutterBottom>
              Tags
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2, alignItems: 'center' }}>
              <TextField
                size="small"
                placeholder="Add tag"
                value={currentTag}
                onChange={(e) => setCurrentTag(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleAddTag();
                  }
                }}
              />
              <Button
                variant="outlined"
                size="small"
                onClick={handleAddTag}
                startIcon={<Add />}
              >
                Add
              </Button>
            </Box>

            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 3 }}>
              {tags.map((tag) => (
                <Chip
                  key={tag}
                  label={tag}
                  onDelete={() => handleRemoveTag(tag)}
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Box>

            {/* Upload Button */}
            <Button
              variant="contained"
              size="large"
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              startIcon={<CloudUpload />}
              fullWidth
            >
              {uploading ? 'Uploading...' : 'Upload File'}
            </Button>

            {uploading && (
              <Box sx={{ mt: 2 }}>
                <LinearProgress variant="determinate" value={uploadProgress} />
                <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
                  {uploadProgress}% uploaded
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Upload Guidelines */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Upload Guidelines
            </Typography>
            <Typography variant="body2" paragraph>
              <strong>File Types:</strong> PDF, Word documents, Excel spreadsheets, images (PNG, JPG, GIF), and text files
            </Typography>
            <Typography variant="body2" paragraph>
              <strong>Maximum Size:</strong> 100 MB per file
            </Typography>
            <Typography variant="body2" paragraph>
              <strong>XML Metadata:</strong> Optionally upload an XML file containing metadata information about your file
            </Typography>
            <Typography variant="body2" paragraph>
              <strong>Tags:</strong> Add relevant tags to help categorize and find your files later
            </Typography>
            <Typography variant="body2">
              <strong>Security:</strong> All files are encrypted and stored securely with tenant isolation
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Upload; 