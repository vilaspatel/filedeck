import React from 'react';
import {
  Box,
  Button,
  Container,
  Typography,
  Paper,
  Grid,
} from '@mui/material';
import { Microsoft } from '@mui/icons-material';
import { useMsal } from '@azure/msal-react';
import { loginRequest } from '../config/authConfig';

const Login: React.FC = () => {
  const { instance } = useMsal();

  const handleLogin = async () => {
    try {
      await instance.loginPopup(loginRequest);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <Container component="main" maxWidth="md" sx={{ height: '100vh', display: 'flex', alignItems: 'center' }}>
      <Grid container spacing={4} alignItems="center">
        <Grid item xs={12} md={6}>
          <Box>
            <Typography variant="h2" component="h1" gutterBottom fontWeight="bold">
              Content Manager
            </Typography>
            <Typography variant="h5" component="h2" color="text.secondary" gutterBottom>
              A comprehensive content management system
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              Manage your files with multi-tenant support, configurable storage options, 
              and powerful metadata management. Upload files with XML metadata, 
              query your content, and download files securely.
            </Typography>
          </Box>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper
            elevation={6}
            sx={{
              p: 4,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
              color: 'white',
            }}
          >
            <Typography variant="h4" component="h1" gutterBottom>
              Welcome
            </Typography>
            <Typography variant="body1" align="center" paragraph>
              Sign in with your organizational account to access the Content Manager
            </Typography>
            <Button
              variant="contained"
              size="large"
              startIcon={<Microsoft />}
              onClick={handleLogin}
              sx={{
                mt: 3,
                mb: 2,
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.3)',
                },
              }}
            >
              Sign in with Microsoft
            </Button>
            <Typography variant="body2" align="center" sx={{ mt: 2, opacity: 0.8 }}>
              Secure authentication powered by Azure Active Directory
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Login; 