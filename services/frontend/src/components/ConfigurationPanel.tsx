import React, {useEffect, useState} from 'react';
import { Container, Card, CardContent, Typography, Select, MenuItem, FormControl, InputLabel, Box } from '@mui/material';
import ScatterPlot from './ScatterPlot';
import LinePlot from './LinePlot';
import BarChart from './BarChart';

function ConfigurationPanel() {
    const [categories, setCategories] = useState({
        values: ['All', 'tech', 'health', 'bank'],
        selectedValue: 'All'
    });

    const [companies, setCompanies] = useState({
        values: Array.from({ length: 15 }, (_, i) => i + 1),
        names: ['alphabet', 'apple', 'amazon', 'microsoft', 'meta', 'united health',
            'johnson and johnson', 'pfizer', 'cvs health', 'mckesson', 'ubs',
            'credit suisse', 'jp morgan', 'goldman sachs', 'bank of america'],
        selectedValue: 1
    });

    const [algorithm, setAlgorithm] = useState({
        values: ['none', 'random', 'regression'],
        selectedValue: 'none'
    });

    const [poem, setPoem] = useState<string | null>(null);

    const [task, setTask] = useState({
        values: ['none', 'poem', 'comparison'],
        selectedValue: 'none'
    });

    const changeCurrentlySelectedCompany = (companyId: number) => {
        setCompanies(prev => ({ ...prev, selectedValue: companyId }));
        if (task.selectedValue !== 'none') {
            changeCurrentlySelectedTask(companyId, task.selectedValue);
        }
    };

    const changeCurrentlySelectedTask = (companyId: number, task: string)=> {
        setTask(prev => ({ ...prev, selectedValue: task }));
        if (task === 'poem' || task === 'comparison') {
            fetchPoem();
        } else {
            setPoem('none');
        }
    };

    useEffect(() => {
        fetchPoem();
    }, [task.selectedValue, companies.selectedValue]);

    const fetchPoem =  async () => {
        try {
            const response = await fetch(`http://127.0.0.1:5000/llm/groq/${task.selectedValue}/${companies.selectedValue}`);
            setPoem(await response.json());
        } catch (error) {
            console.error("Error fetching the poem:", error);
        }
    }


    return (
        <Container maxWidth={false} sx={{ mt: 2 }}>
            <Box
                sx={{
                    display: 'grid',
                    gridTemplateColumns: { xs: '1fr', md: '1.5fr 4fr 4fr 4fr' },
                    gap: 2
                }}
            >
                <Card sx={{
                    borderRight: '1px solid rgba(0, 0, 0, 0.1)',
                    background: 'lightpink',
                    paddingLeft: 'auto',
                    height: 'calc(100vh - 50px)'
                }}>
                    <CardContent>
                        <Typography variant="h6" sx={{
                            fontFamily: '"Open Sans", verdana, arial, sans-serif',
                            fontSize: '15px',
                            borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
                            display: 'flex',
                            fontWeight: 500,
                            height: '40px',
                            alignItems: 'center',
                            mb: 2
                        }}>
                            Company Overview
                        </Typography>

                        <FormControl fullWidth sx={{ mb: 3 }}>
                            <InputLabel>Select a category</InputLabel>
                            <Select
                                value={categories.selectedValue}
                                label="Select a category"
                                onChange={(e) => {
                                    const newCategory = e.target.value;
                                    setCategories(prev => ({ ...prev, selectedValue: newCategory }));
                                }}
                                size="small"
                            >

                            {categories.values.map((category) => (
                                    <MenuItem key={category} value={category}>
                                        {category}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>

                        <Typography variant="h6" sx={{
                            fontFamily: '"Open Sans", verdana, arial, sans-serif',
                            fontSize: '15px',
                            borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
                            display: 'flex',
                            fontWeight: 500,
                            height: '40px',
                            alignItems: 'center',
                            mb: 2
                        }}>
                            Profit View
                        </Typography>

                        <FormControl fullWidth sx={{ mb: 2 }}>
                            <InputLabel>Select a company</InputLabel>
                            <Select
                                value={companies.selectedValue}
                                label="Select a company"
                                onChange={(e) => {
                                    const newCompany = parseInt(e.target.value.toString());
                                    setCompanies(prev => ({ ...prev, selectedValue: newCompany }));
                                }}
                                size="small"
                            >
                                {companies.values.map((company) => (
                                    <MenuItem key={company} value={company}>
                                        {companies.names[company-1]}
                                    </MenuItem>
                                ))}
                            </Select>

                        </FormControl>

                        <FormControl fullWidth>
                            <InputLabel>Select an algorithm</InputLabel>
                            <Select
                                value={algorithm.selectedValue}
                                label="Select an algorithm"
                                onChange={(e) => {
                                    const newAlgorithm = e.target.value;
                                    setAlgorithm(prev => ({ ...prev, selectedValue: newAlgorithm }));
                                }}
                                size="small"
                            >
                                {algorithm.values.map((algo) => (
                                    <MenuItem key={algo} value={algo}>
                                        {algo}
                                    </MenuItem>
                                ))}
                            </Select>

                        </FormControl>
                    </CardContent>
                </Card>

                <ScatterPlot
                    selectedCategory={categories.selectedValue}
                    onCompanyChange={changeCurrentlySelectedCompany}
                />

                <LinePlot
                    selectedCompany={companies.selectedValue}
                    selectedAlgorithm={algorithm.selectedValue}
                />

                <BarChart
                    selectedCompany={companies.selectedValue}
                    onCompanyChange={changeCurrentlySelectedCompany}
                />
            </Box>
            <Box
                sx={{
                    display: 'grid',
                    gridTemplateColumns: { xs: '1fr', md: '1.5fr 12fr' },
                    gap: 2
                }}
            >
                <Card sx={{
                    borderRight: '1px solid rgba(0, 0, 0, 0.1)',
                    background: '#b9e4ff',
                    paddingLeft: 'auto',
                    height: 'calc(100vh - 50px)'
                }}>
                    <CardContent>
                        <Typography variant="h6" sx={{
                            fontFamily: '"Open Sans", verdana, arial, sans-serif',
                            fontSize: '15px',
                            borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
                            display: 'flex',
                            fontWeight: 500,
                            height: '40px',
                            alignItems: 'center',
                            mb: 2
                        }}>
                            AI Interaction
                        </Typography>

                        <FormControl fullWidth sx={{ mb: 3 }}>
                            <InputLabel>Select a company</InputLabel>
                            <Select
                                value={companies.selectedValue}
                                label="Select a company"
                                onChange={(e) => {
                                    const newCompany = parseInt(e.target.value.toString());
                                    setCompanies(prev => ({ ...prev, selectedValue: newCompany }));
                                }}
                                size="small"
                            >
                                {companies.values.map((company) => (
                                    <MenuItem key={company} value={company}>
                                        {companies.names[company-1]}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                        <FormControl fullWidth sx={{ mb: 3 }}>
                            <InputLabel>Select a task</InputLabel>
                            <Select
                                value={task.selectedValue}
                                label="Select a task"
                                onChange={(e) => {
                                    const newTask = e.target.value.toString();
                                    setTask(prev => ({...prev, selectedValue: newTask}));
                                }}
                                size="small"
                                >
                                {task.values.map((task) => (
                                    <MenuItem key={task} value={task}>
                                        {task}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </CardContent>
                </Card>
                <Card sx={{
                    borderRight: '1px solid rgba(0, 0, 0, 0.1)',
                    background: '#b6b6fa',
                    paddingleft: 'auto',
                    height: 'auto'
                }}>
                    <CardContent>
                        <Typography sx={{ fontWeight: 'bold' }}>
                            AI Generated {task.selectedValue === 'poem' ? 'Poem' : task.selectedValue === 'comparison' ? 'Comparison' : 'Overview'} for {companies.names[companies.selectedValue-1]}
                        </Typography>
                        <Typography variant="h6" sx={{
                            fontFamily: '"Open Sans", verdana, arial, sans-serif',
                            fontSize: '15px',
                            borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
                            display: 'flex',
                            fontWeight: 500,
                            height: 'auto',
                            alignItems: 'center',
                            mb: 2,
                            whiteSpace: 'pre-line'
                        }}>
                            {poem ? poem : null}
                        </Typography>
                    </CardContent>
                </Card>
            </Box>

        </Container>
    );
}

export default ConfigurationPanel;
