import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Paper, Typography, Box, Grid, Button, 
  List, ListItem, ListItemText,
  CircularProgress
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import EducationScore from '../components/EducationScore';
import CourseRecommendations from '../components/CourseRecommendations';

const roleNames = {
  'data_scientist': 'Data Scientist',
  'data_engineer': 'Инженер данных',
  'technical_analyst': 'Технический аналитик',
  'ai_manager': 'AI менеджер',
  'ml_engineer': 'ML инженер',
  'data_architect': 'Архитектор данных',
  'business_intelligence_analyst': 'BI аналитик',
  'research_scientist': 'Научный сотрудник'
};

function AnalysisResults() {
  const { id } = useParams();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/analysis/${id}`);
        setResults(response.data);
      } catch (err) {
        setError('Ошибка при загрузке результатов анализа');
        console.error('Error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, [id]);

  if (loading) return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
      <CircularProgress />
    </Box>
  );

  if (error) return <Typography color="error">{error}</Typography>;
  if (!results) return <Typography>Результаты не найдены</Typography>;

  const chartData = Object.entries(results.role_matches)
    .sort(([, a], [, b]) => b - a)
    .map(([role, percentage]) => ({
      role: roleNames[role] || role,
      percentage: percentage
    }));

  return (
    <Paper sx={{ p: 4 }}>
      {/* Основная информация */}
      <Box mb={4}>
        <Typography variant="h5" gutterBottom>
          Информация о кандидате
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="body1" gutterBottom>
              <strong>ФИО:</strong> {results.personal_data.name}
            </Typography>
            <Typography variant="body1" gutterBottom>
              <strong>Email:</strong> {results.personal_data.email}
            </Typography>
            <Typography variant="body1" gutterBottom>
              <strong>Образование:</strong> {results.education.university}
            </Typography>
            <Typography variant="body1">
              <strong>Период обучения:</strong> {results.education.years}
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box textAlign="center">
              <Typography variant="h6" gutterBottom>
                Общий балл
              </Typography>
              <Typography variant="h3" color="primary">
                {results.base_score}/100
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Box>

      {/* График совместимости с ролями */}
      <Box mb={4}>
        <Typography variant="h5" gutterBottom>
          Совместимость с ролями
        </Typography>
        <Box height={400}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical" margin={{ left: 150 }}>
              <XAxis type="number" domain={[0, 100]} />
              <YAxis dataKey="role" type="category" width={150} />
              <Tooltip />
              <Bar dataKey="percentage" fill="#2196f3" />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </Box>

      {/* Детальный анализ навыков */}
      <Box mb={4}>
        <Typography variant="h5" gutterBottom>
          Анализ навыков по отраслям
        </Typography>
        <Grid container spacing={3}>
          {Object.entries(results.industry_relevance).map(([industry, skills]) => (
            <Grid item xs={12} md={6} key={industry}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" gutterBottom>{industry}</Typography>
                <List>
                  {skills.map((skill) => (
                    <ListItem key={skill.skill}>
                      <ListItemText
                        primary={skill.skill}
                        secondary={skill.description}
                      />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Рекомендации по развитию */}
      <Box mb={4}>
        <Typography variant="h5" gutterBottom>
          Рекомендации по развитию
        </Typography>
        <Grid container spacing={3}>
          {Object.entries(results.missing_skills).map(([role, skills]) => (
            <Grid item xs={12} md={6} key={role}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" gutterBottom>{roleNames[role] || role}</Typography>
                <List>
                  {skills.map((skill) => (
                    <ListItem key={skill}>
                      <ListItemText primary={skill} />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Рекомендуемые курсы */}
      <Box>
        <Typography variant="h5" gutterBottom>
          Рекомендуемые курсы
        </Typography>
        <Grid container spacing={3}>
          {results.learning_recommendations.map((course, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" gutterBottom>{course.title}</Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  {course.description}
                </Typography>
                <Typography variant="body2">
                  <strong>Платформа:</strong> {course.platform}
                </Typography>
                <Typography variant="body2">
                  <strong>Длительность:</strong> {course.duration}
                </Typography>
                <Box mt={2}>
                  <Button 
                    variant="contained" 
                    color="primary"
                    href={course.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Перейти к курсу
                  </Button>
                </Box>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Paper>
  );
}

export default AnalysisResults;
