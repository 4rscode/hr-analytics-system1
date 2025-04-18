import { Box, Typography, Card, Grid, Container } from '@mui/material';
import ResumeUpload from '../components/ResumeUpload';
import { ThemeProvider } from '@mui/material/styles';
import theme from '../theme';

export default function Home() {
  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom align="center">
            HR Analytics System
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={8} mx="auto">
              <Card sx={{ p: 3 }}>
                <ResumeUpload />
              </Card>
            </Grid>
          </Grid>
        </Box>
      </Container>
    </ThemeProvider>
  );
}
