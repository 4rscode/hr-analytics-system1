import { Box, Typography, Tooltip } from '@mui/material';

function EducationScore({ education }) {
  const getScoreColor = (score) => {
    if (score >= 90) return '#4caf50';
    if (score >= 70) return '#2196f3';
    if (score >= 50) return '#ff9800';
    return '#f44336';
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Оценка образования
      </Typography>
      <Tooltip title={`${education.university} (${education.rank})`}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 2
          }}
        >
          <Typography>
            {education.score}/100
          </Typography>
          <Box
            sx={{
              width: 200,
              height: 8,
              bgcolor: '#eee',
              borderRadius: 4,
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            <Box
              sx={{
                position: 'absolute',
                width: `${education.score}%`,
                height: '100%',
                bgcolor: getScoreColor(education.score),
                transition: 'width 0.5s ease-in-out'
              }}
            />
          </Box>
        </Box>
      </Tooltip>
    </Box>
  );
}

export default EducationScore;
