import { Paper, Button, Typography, Box, IconButton } from '@mui/material';
import { CloudUpload, Close as CloseIcon } from '@mui/icons-material';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const navigate = useNavigate();

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/api/upload', formData);
      navigate(`/analysis/${response.data.resume_id}`);
    } catch (error) {
      console.error('Ошибка при загрузке файла:', error);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" align="center" gutterBottom>
        HR Аналитика
      </Typography>
      <Typography variant="subtitle1" align="center" color="textSecondary" gutterBottom>
        Загрузите резюме для анализа компетенций кандидата
      </Typography>
      
      <Paper 
        sx={{ 
          p: 4, 
          mt: 4,
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          border: '2px dashed',
          borderColor: dragActive ? 'primary.main' : 'grey.300',
          backgroundColor: dragActive ? 'action.hover' : 'background.paper',
          transition: 'all 0.3s ease-in-out'
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          accept=".pdf,.docx"
          style={{ display: 'none' }}
          id="resume-file"
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
        />
        
        {!file ? (
          <>
            <CloudUpload sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom align="center">
              Перетащите резюме сюда
            </Typography>
            <Typography variant="body1" color="textSecondary" align="center" gutterBottom>
              или
            </Typography>
            <label htmlFor="resume-file">
              <Button
                variant="contained"
                component="span"
                startIcon={<CloudUpload />}
              >
                Выберите файл
              </Button>
            </label>
            <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
              Поддерживаемые форматы: PDF, DOCX
            </Typography>
          </>
        ) : (
          <Box sx={{ width: '100%', textAlign: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
              <Typography variant="body1">
                Выбран файл: {file.name}
              </Typography>
              <IconButton 
                size="small" 
                onClick={() => setFile(null)}
                sx={{ ml: 1 }}
              >
                <CloseIcon />
              </IconButton>
            </Box>
            <Button
              variant="contained"
              color="primary"
              onClick={handleUpload}
              size="large"
            >
              Анализировать резюме
            </Button>
          </Box>
        )}
      </Paper>
    </Box>
  );
}

export default ResumeUpload;
