import { AppBar, Toolbar, Typography, Container, Box } from '@mui/material';
import { Link } from 'react-router-dom';

function Layout({ children }) {
  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component={Link} to="/" sx={{ textDecoration: 'none', color: 'inherit' }}>
            HR Аналитика
          </Typography>
          <Box sx={{ marginLeft: 'auto' }}>
            <Typography 
              component={Link} 
              to="/history" 
              sx={{ textDecoration: 'none', color: 'inherit', marginRight: 2 }}
            >
              История анализов
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {children}
      </Container>
    </>
  );
}

export default Layout;
