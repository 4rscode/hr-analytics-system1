import { useState } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  CircularProgress, 
  Card, 
  CardContent, 
  List, 
  ListItem, 
  ListItemText, 
  Chip, 
  Divider,
  Grid,
  Paper,
  Link
} from '@mui/material';
import { CloudUpload } from '@mui/icons-material';
import axios from 'axios';

export default function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/upload', formData);
      setResults(response.data);
    } catch (error) {
      console.error('Ошибка:', error);
      alert('Ошибка при загрузке файла');
    } finally {
      setLoading(false);
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

  const renderBestRole = (roleFit) => {
    const roleNames = {
      'data_scientist': 'Data Scientist',
      'data_engineer': 'Data Engineer',
      'technical_analyst': 'Технический аналитик',
      'ai_manager': 'AI менеджер',
      'ml_engineer': 'ML инженер',
      'data_architect': 'Архитектор данных',
      'business_intelligence_analyst': 'BI аналитик',
      'research_scientist': 'Научный сотрудник'
    };

    return (
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" color="primary" gutterBottom>
          {roleNames[roleFit.best_fit.role] || roleFit.best_fit.role} ({roleFit.best_fit.score.toFixed(1)}%)
        </Typography>
      </Box>
    );
  };

  const renderAllRoles = (roleFit) => {
    const roleNames = {
      'data_scientist': 'Data Scientist',
      'data_engineer': 'Data Engineer',
      'technical_analyst': 'Технический аналитик',
      'ai_manager': 'AI менеджер',
      'ml_engineer': 'ML инженер',
      'data_architect': 'Архитектор данных',
      'business_intelligence_analyst': 'BI аналитик',
      'research_scientist': 'Научный сотрудник'
    };

    return (
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>Все роли</Typography>
        <Grid container spacing={2}>
          {Object.entries(roleFit.all_roles)
            .sort(([, a], [, b]) => b - a)
            .map(([role, score]) => (
              <Grid item xs={12} sm={6} md={4} key={role}>
                <Paper 
                  sx={{ 
                    p: 2, 
                    textAlign: 'center',
                    backgroundColor: '#f5f5f5',
                    borderRadius: 2
                  }}
                >
                  <Typography variant="subtitle1">{roleNames[role] || role}</Typography>
                  <Typography variant="h6" color="primary">{score.toFixed(1)}%</Typography>
                </Paper>
              </Grid>
            ))}
        </Grid>
      </Box>
    );
  };

  const renderDetailedAnalysis = (details) => {
    const categoryNames = {
      'education': 'Образование',
      'experience': 'Опыт',
      'skills': 'Навыки',
      'languages': 'Языки'
    };

    return (
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>Детальный анализ</Typography>
        <Grid container spacing={2}>
          {Object.entries(details).map(([category, data]) => (
            <Grid item xs={12} sm={6} md={3} key={category}>
              <Paper 
                sx={{ 
                  p: 3, 
                  textAlign: 'center',
                  backgroundColor: '#f5f5f5',
                  borderRadius: 2,
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center'
                }}
              >
                <Typography variant="subtitle1" gutterBottom>
                  {categoryNames[category] || category}
                </Typography>
                <Typography variant="h3" color="primary">
                  {data.score ? data.score.toFixed(1) : '0'}%
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  };

  const renderRecommendations = (recommendations) => {
    const categoryTitles = {
      'education': 'Образование',
      'experience': 'Опыт работы',
      'skills': 'Навыки',
      'languages': 'Языки'
    };

    return (
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>Рекомендации</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, height: '100%', backgroundColor: '#f5f5f5', borderRadius: 2 }}>
              <Typography variant="subtitle1" gutterBottom>Области для улучшения</Typography>
              <List>
                {Object.entries(recommendations).map(([category, items]) => {
                  if (Array.isArray(items) && items.length > 0 && category !== 'course_recommendations') {
                    return items.map((item, index) => (
                      <ListItem key={`${category}-${index}`}>
                        <ListItemText
                          primary={categoryTitles[category]}
                          secondary={item}
                        />
                      </ListItem>
                    ));
                  }
                  return null;
                })}
              </List>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, height: '100%', backgroundColor: '#f5f5f5', borderRadius: 2 }}>
              <Typography variant="subtitle1" gutterBottom>Рекомендуемые курсы</Typography>
              <List>
                {recommendations.course_recommendations?.map((course, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={course.name}
                      secondary={
                        <>
                          {`${course.platform} | ${course.duration} | ${course.level}`}
                          <br />
                          <Link 
                            href={course.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            sx={{ mt: 1 }}
                          >
                            Подробнее о курсе
                          </Link>
                        </>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    );
  };

  if (loading) {
    return (
      <Box display="flex" flexDirection="column" alignItems="center" mt={4}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Анализируем резюме...
        </Typography>
      </Box>
    );
  }

  if (results) {
    return (
      <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
        <Typography variant="h4" align="center" gutterBottom>
          Результаты анализа
        </Typography>
        
        {/* Общий балл */}
        <Card sx={{ mb: 4, backgroundColor: '#f5f5f5' }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Общий балл
            </Typography>
            <Typography variant="h3" color="primary">
              {results.base_score}/100
            </Typography>
          </CardContent>
        </Card>

        {/* Наиболее подходящая роль */}
        <Typography variant="h5" gutterBottom>
          Наиболее подходящая роль
        </Typography>
        {results.role_fit && renderBestRole(results.role_fit)}

        {/* Все роли */}
        {results.role_fit && renderAllRoles(results.role_fit)}

        {/* Детальный анализ */}
        {results.detailed_analysis && renderDetailedAnalysis(results.detailed_analysis)}

        {/* Рекомендации */}
        {results.recommendations && renderRecommendations(results.recommendations)}

        {/* Кнопка для нового анализа */}
        <Box textAlign="center" mt={4}>
          <Button
            variant="contained"
            color="primary"
            onClick={() => {
              setFile(null);
              setResults(null);
            }}
          >
            Загрузить другое резюме
          </Button>
        </Box>
      </Box>
    );
  }

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
          transition: 'all 0.3s ease-in-out',
          cursor: 'pointer'
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
            <Typography variant="body1" gutterBottom>
              Выбран файл: {file.name}
            </Typography>
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
