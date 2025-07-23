import React from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
} from '@mui/material';
import {
  CloudUpload,
  Folder,
  Storage,
  People,
} from '@mui/icons-material';

const StatCard: React.FC<{
  title: string;
  value: string;
  icon: React.ReactNode;
  color: string;
}> = ({ title, value, icon, color }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box>
          <Typography color="textSecondary" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h4" component="div">
            {value}
          </Typography>
        </Box>
        <Box
          sx={{
            backgroundColor: color,
            borderRadius: '50%',
            p: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

const Dashboard: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Statistics Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Files"
            value="1,234"
            icon={<Folder sx={{ color: 'white' }} />}
            color="#2196F3"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Uploads Today"
            value="45"
            icon={<CloudUpload sx={{ color: 'white' }} />}
            color="#4CAF50"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Storage Used"
            value="2.5 GB"
            icon={<Storage sx={{ color: 'white' }} />}
            color="#FF9800"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Users"
            value="28"
            icon={<People sx={{ color: 'white' }} />}
            color="#9C27B0"
          />
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Box sx={{ mt: 2 }}>
              {[
                { action: 'File uploaded', file: 'document.pdf', time: '2 minutes ago' },
                { action: 'File downloaded', file: 'spreadsheet.xlsx', time: '5 minutes ago' },
                { action: 'Metadata updated', file: 'image.jpg', time: '10 minutes ago' },
                { action: 'File shared', file: 'presentation.pptx', time: '15 minutes ago' },
              ].map((activity, index) => (
                <Box
                  key={index}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    py: 1,
                    borderBottom: index < 3 ? '1px solid #eee' : 'none',
                  }}
                >
                  <Box>
                    <Typography variant="body2">
                      <strong>{activity.action}</strong> - {activity.file}
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="textSecondary">
                    {activity.time}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* Storage Overview */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Storage Overview
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Used: 2.5 GB of 10 GB
              </Typography>
              <LinearProgress
                variant="determinate"
                value={25}
                sx={{ height: 8, borderRadius: 4 }}
              />
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2">
                  • Documents: 1.2 GB
                </Typography>
                <Typography variant="body2">
                  • Images: 0.8 GB
                </Typography>
                <Typography variant="body2">
                  • Other: 0.5 GB
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item>
                <Card
                  sx={{
                    p: 2,
                    textAlign: 'center',
                    cursor: 'pointer',
                    '&:hover': { backgroundColor: '#f5f5f5' },
                  }}
                >
                  <CloudUpload sx={{ fontSize: 40, color: '#2196F3', mb: 1 }} />
                  <Typography variant="body2">Upload Files</Typography>
                </Card>
              </Grid>
              <Grid item>
                <Card
                  sx={{
                    p: 2,
                    textAlign: 'center',
                    cursor: 'pointer',
                    '&:hover': { backgroundColor: '#f5f5f5' },
                  }}
                >
                  <Folder sx={{ fontSize: 40, color: '#4CAF50', mb: 1 }} />
                  <Typography variant="body2">Browse Files</Typography>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 