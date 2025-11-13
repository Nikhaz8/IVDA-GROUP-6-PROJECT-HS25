import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import ConfigurationPanel from './components/ConfigurationPanel';
import './App.css';

function App() {
    return (
        <Box sx={{ flexGrow: 1, background: '#c1c1c1' }}>
            <AppBar position="static" color="primary">
                <Toolbar sx = {{ bgcolor: 'black' }}>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1}}>
                        Nikhaz Omar 25-743-147
                    </Typography>
                </Toolbar>
            </AppBar>
            <ConfigurationPanel />
        </Box>
    );
}

export default App;
