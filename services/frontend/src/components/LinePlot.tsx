import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@mui/material';
import Plot from 'react-plotly.js';

interface LinePlotProps {
    selectedCompany: number;
    selectedAlgorithm: string;
}

function LinePlot({ selectedCompany, selectedAlgorithm }: LinePlotProps) {
    // Use selectedCompany and selectedAlgorithm in useEffect dependency
    useEffect(() => {
        fetchData();
    }, [selectedCompany, selectedAlgorithm]);

    const [lineData, setLineData] = useState({ x: [] as number[], y: [] as number[], name: [] as string[] });

    const fetchData = async () => {
        try {
            // req URL to retrieve single company from backend
            const reqUrl = `http://127.0.0.1:5000/companies/${selectedCompany}?algorithm=${selectedAlgorithm}`;
            console.log("ReqURL " + reqUrl);

            // await response and data
            const response = await fetch(reqUrl);
            const responseData = await response.json();

            // transform data to usable by lineplot
            const xData: number[] = [];
            const yData: number[] = [];
            const nameData= responseData.name;

            responseData.profit.forEach((profit: any) => {
                xData.push(profit.year);
                yData.push(profit.value);
            });

            setLineData({ x: xData, y: yData, name: nameData });
        } catch (error) {
            console.error('Error fetching company profit data:', error);
        }
    };

    const data1 = {
        x: selectedAlgorithm === 'none' ? lineData.x : lineData.x.slice(1, lineData.x.length),
        y: selectedAlgorithm === 'none' ? lineData.y : lineData.y.slice(1, lineData.y.length),
        mode: 'lines+markers' as const,
        type: 'scatter' as const,
        marker: { color: 'default' },
        name: 'Profit'
    };

    const data2 = {
        x: lineData.x.slice(0, 2),
        y: lineData.y.slice(0, 2),
        mode: 'lines+markers' as const,
        type: 'scatter' as const,
        marker: { color: 'lightgreen' },
        line: { dash: 'dashdot' },
        name: 'Projection'
    };

    const data = selectedAlgorithm === 'none' ? [data1] : [data2, data1];

    const layout = {
        title: {text: `Profit View of Company: ${lineData.name}`},
        height: window.innerHeight * 0.9,
        xaxis: { title: {text: 'Year'} },
        yaxis: { title: {text: 'Profit'} }
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    return (
        <Card>
            <CardContent sx={{ p: 0 }}>
                <Plot
                    data={data as any}
                    layout={layout as any}
                    config={config}
                    style={{ width: '100%', height: '90vh' }}
                    useResizeHandler={true}
                ></Plot>
            </CardContent>
        </Card>
    );
}

export default LinePlot;

