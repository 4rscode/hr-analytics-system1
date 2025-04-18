import { useState, useEffect } from 'react';
import {
  Paper, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Dialog, DialogContent, DialogTitle,
  Button, Typography, Box
} from '@mui/material';
import axios from 'axios';
import AnalysisResults from './AnalysisResults';

function ResumeHistory() {
  const [resumes, setResumes] = useState([]);
  const [selectedResume, setSelectedResume] = useState(null);

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

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/history');
        setResumes(response.data);
      } catch (error) {
        console.error('Ошибка при загрузке истории:', error);
      }
    };
    fetchHistory();
  }, []);

  const formatRoleMatches = (roleMatches) => {
    return Object.entries(roleMatches)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([role, percentage]) => (
        <Box key={role} sx={{ mb: 0.5 }}>
          <Typography variant="body2">
            {roleNames[role] || role}: {percentage.toFixed(1)}%
          </Typography>
        </Box>
      ));
  };

  return (
    <>
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        История анализа резюме
      </Typography>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ФИО кандидата</TableCell>
              <TableCell>Файл резюме</TableCell>
              <TableCell>Дата загрузки</TableCell>
              <TableCell>Топ-3 подходящих роли</TableCell>
              <TableCell>Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {resumes.map((resume) => (
              <TableRow 
                key={resume.id}
                sx={{ '&:hover': { backgroundColor: '#f5f5f5' } }}
              >
                <TableCell>{resume.name}</TableCell>
                <TableCell>{resume.filename}</TableCell>
                <TableCell>
                  {new Date(resume.upload_date).toLocaleDateString('ru-RU', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </TableCell>
                <TableCell>
                  {formatRoleMatches(resume.analysis_results.role_matches)}
                </TableCell>
                <TableCell>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => setSelectedResume(resume)}
                  >
                    Подробнее
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog
        open={Boolean(selectedResume)}
        onClose={() => setSelectedResume(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Детальный анализ резюме
          <Typography variant="subtitle1" color="textSecondary">
            {selectedResume?.name}
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedResume && <AnalysisResults resumeId={selectedResume.id} />}
        </DialogContent>
      </Dialog>
    </>
  );
}

export default ResumeHistory;
