import { Box, Typography, Card, CardContent, Button, Grid } from '@mui/material';

function CourseRecommendations({ recommendations }) {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Рекомендуемые курсы
      </Typography>
      <Grid container spacing={2}>
        {recommendations.map((course) => (
          <Grid item xs={12} md={6} key={course.name}>
            <Card>
              <CardContent>
                <Typography variant="h6">{course.name}</Typography>
                <Typography color="textSecondary">
                  Платформа: {course.platform}
                </Typography>
                <Typography>
                  Длительность: {course.duration}
                </Typography>
                <Button 
                  variant="contained" 
                  href={course.url}
                  target="_blank"
                  sx={{ mt: 1 }}
                >
                  Перейти к курсу
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default CourseRecommendations;
