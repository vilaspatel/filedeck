import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Save,
  Storage,
  Database,
  Security,
} from '@mui/icons-material';

const Settings: React.FC = () => {
  const [storageType, setStorageType] = useState('azure');
  const [databaseType, setDatabaseType] = useState('postgresql');
  const [notifications, setNotifications] = useState(true);
  const [autoBackup, setAutoBackup] = useState(false);

  const handleSave = () => {
    console.log('Saving settings...');
    // TODO: Implement settings save
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>

      <Grid container spacing={3}>
        {/* Storage Configuration */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Storage sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Storage Configuration</Typography>
            </Box>
            
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Storage Provider</InputLabel>
              <Select
                value={storageType}
                label="Storage Provider"
                onChange={(e) => setStorageType(e.target.value)}
              >
                <MenuItem value="azure">Azure Blob Storage</MenuItem>
                <MenuItem value="gcp">Google Cloud Storage</MenuItem>
                <MenuItem value="aws">AWS S3</MenuItem>
                <MenuItem value="local">Local Storage</MenuItem>
              </Select>
            </FormControl>

            {storageType === 'azure' && (
              <>
                <TextField
                  fullWidth
                  label="Storage Account Name"
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Container Name"
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Access Key"
                  type="password"
                  sx={{ mb: 2 }}
                />
              </>
            )}

            {storageType === 'gcp' && (
              <>
                <TextField
                  fullWidth
                  label="Project ID"
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Bucket Name"
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Service Account Key Path"
                  sx={{ mb: 2 }}
                />
              </>
            )}

            {storageType === 'aws' && (
              <>
                <TextField
                  fullWidth
                  label="Access Key ID"
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Secret Access Key"
                  type="password"
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Bucket Name"
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Region"
                  sx={{ mb: 2 }}
                />
              </>
            )}
          </Paper>
        </Grid>

        {/* Database Configuration */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Database sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Database Configuration</Typography>
            </Box>
            
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Database Type</InputLabel>
              <Select
                value={databaseType}
                label="Database Type"
                onChange={(e) => setDatabaseType(e.target.value)}
              >
                <MenuItem value="postgresql">PostgreSQL</MenuItem>
                <MenuItem value="mysql">MySQL</MenuItem>
                <MenuItem value="sqlite">SQLite</MenuItem>
                <MenuItem value="mongodb">MongoDB</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Database URL"
              placeholder="postgresql://user:password@localhost:5432/database"
              sx={{ mb: 2 }}
            />
            
            <Alert severity="info" sx={{ mb: 2 }}>
              Database changes require application restart
            </Alert>
          </Paper>
        </Grid>

        {/* Security & Authentication */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Security sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Azure AD Configuration</Typography>
            </Box>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Tenant ID"
                  sx={{ mb: 2 }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Client ID"
                  sx={{ mb: 2 }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Client Secret"
                  type="password"
                  sx={{ mb: 2 }}
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Application Settings */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Application Settings
            </Typography>
            
            <FormControlLabel
              control={
                <Switch
                  checked={notifications}
                  onChange={(e) => setNotifications(e.target.checked)}
                />
              }
              label="Enable email notifications"
              sx={{ mb: 2, display: 'block' }}
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={autoBackup}
                  onChange={(e) => setAutoBackup(e.target.checked)}
                />
              }
              label="Enable automatic backups"
              sx={{ mb: 2, display: 'block' }}
            />

            <Divider sx={{ my: 3 }} />

            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={<Save />}
                onClick={handleSave}
              >
                Save Settings
              </Button>
              <Button variant="outlined">
                Reset to Defaults
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Settings; 