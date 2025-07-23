import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  TablePagination,
} from '@mui/material';
import {
  Search,
  Download,
  Visibility,
  Delete,
  FilterList,
} from '@mui/icons-material';

interface FileData {
  id: string;
  filename: string;
  size: string;
  type: string;
  uploadDate: string;
  tags: string[];
}

const mockFiles: FileData[] = [
  {
    id: '1',
    filename: 'project-proposal.pdf',
    size: '2.5 MB',
    type: 'PDF',
    uploadDate: '2023-12-01',
    tags: ['proposal', 'important'],
  },
  {
    id: '2',
    filename: 'financial-report.xlsx',
    size: '1.8 MB',
    type: 'Excel',
    uploadDate: '2023-12-02',
    tags: ['finance', 'report'],
  },
  {
    id: '3',
    filename: 'presentation.pptx',
    size: '5.2 MB',
    type: 'PowerPoint',
    uploadDate: '2023-12-03',
    tags: ['presentation'],
  },
];

const Files: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const handleDownload = (fileId: string) => {
    console.log('Download file:', fileId);
  };

  const handleView = (fileId: string) => {
    console.log('View file:', fileId);
  };

  const handleDelete = (fileId: string) => {
    console.log('Delete file:', fileId);
  };

  const filteredFiles = mockFiles.filter(file =>
    file.filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Files
      </Typography>

      {/* Search and Filter */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
        <TextField
          placeholder="Search files..."
          variant="outlined"
          size="small"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <Search sx={{ mr: 1, color: 'action.active' }} />,
          }}
          sx={{ flexGrow: 1, maxWidth: 400 }}
        />
        <Button
          variant="outlined"
          startIcon={<FilterList />}
        >
          Filters
        </Button>
      </Box>

      {/* Files Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Filename</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Upload Date</TableCell>
              <TableCell>Tags</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredFiles
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((file) => (
                <TableRow key={file.id} hover>
                  <TableCell>{file.filename}</TableCell>
                  <TableCell>{file.size}</TableCell>
                  <TableCell>{file.type}</TableCell>
                  <TableCell>{file.uploadDate}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {file.tags.map((tag) => (
                        <Chip
                          key={tag}
                          label={tag}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton
                        size="small"
                        onClick={() => handleView(file.id)}
                        title="View"
                      >
                        <Visibility />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDownload(file.id)}
                        title="Download"
                      >
                        <Download />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(file.id)}
                        title="Delete"
                        color="error"
                      >
                        <Delete />
                      </IconButton>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredFiles.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          onRowsPerPageChange={(event) => {
            setRowsPerPage(parseInt(event.target.value, 10));
            setPage(0);
          }}
        />
      </TableContainer>
    </Box>
  );
};

export default Files; 