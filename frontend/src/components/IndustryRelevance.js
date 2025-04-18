import { Box, Typography, Card, CardContent, Chip, Grid } from '@mui/material';

function IndustryRelevance({ relevance }) {
  const getIndustryColor = (industry) => {
    const colors = {
      'Нефтегазовая': '#ff9800',
      'Образование': '#2196f3',
      'Сельское хозяйство': '#4caf50',
      'Медицина': '#f44336',
      'Металлургия': '#9c27b0',
      'Девелопмент': '#795548'
    };
    return colors[industry] || '#grey';
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Применимость навыков по отраслям
      </Typography>
      <Grid container spacing={2}>
        {Object.entries(relevance).map(([industry, skills]) => (
          <Grid item xs={12} md={6} key={industry}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {industry}
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {skills.map((skill) => (
                    <Chip 
                      key={skill.skill}
                      label={skill.skill}
                      sx={{ backgroundColor: getIndustryColor(industry) }}
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default IndustryRelevance;
