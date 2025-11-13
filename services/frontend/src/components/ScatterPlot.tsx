import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import Plot from 'react-plotly.js';

interface ScatterPlotProps {
    selectedCategory: string;
    onCompanyChange?: (companyId: number) => void;
}

function ScatterPlot({ selectedCategory, onCompanyChange }: ScatterPlotProps) {

    const [techData, setTechData] = useState({
        x: [] as number[],
        y: [] as number[],
        name: [] as string[],
        category: [] as string[]
    });

    const [bankData, setBankData] = useState({
        x: [] as number[],
        y: [] as number[],
        name: [] as string[],
        category: [] as string[]
    });

    const [healthData, setHealthData] = useState({
        x: [] as number[],
        y: [] as number[],
        name: [] as string[],
        category: [] as string[]
    });

    const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

    useEffect(() => {
        fetchData();
    }, [selectedCategory]); // Re-fetch when category changes

    const fetchData = async () => {
        try {
            // req URL to retrieve companies from backend with category filter
            const reqUrl = `http://127.0.0.1:5000/companies?category=${selectedCategory}`;
            console.log("ReqURL " + reqUrl);

            // await response and data
            const response = await fetch(reqUrl);
            const responseData = await response.json();

            const xDataTech: number[] = [];
            const yDataTech: number[] = [];
            const nameDataTech: string[] = [];
            const categoryDataTech: string[] = [];

            const xDataBank: number[] = [];
            const yDataBank: number[] = [];
            const nameDataBank: string[] = [];
            const categoryDataBank: string[] = [];

            const xDataHealth: number[] = [];
            const yDataHealth: number[] = [];
            const nameDataHealth: string[] = [];
            const categoryDataHealth: string[] = [];

            responseData.forEach((company: any) => {
                if (company.category === 'tech') {
                    xDataTech.push(company.founding_year);
                    yDataTech.push(company.employees);
                    nameDataTech.push(company.name);
                    categoryDataTech.push(company.category);
                } else if (company.category === 'bank') {
                    xDataBank.push(company.founding_year);
                    yDataBank.push(company.employees);
                    nameDataBank.push(company.name);
                    categoryDataBank.push(company.category);
                } else if (company.category === 'health') {
                    xDataHealth.push(company.founding_year);
                    yDataHealth.push(company.employees);
                    nameDataHealth.push(company.name);
                    categoryDataHealth.push(company.category);
                }
            });
            setTechData({ x: xDataTech, y: yDataTech, name: nameDataTech, category: categoryDataTech });
            setBankData({ x: xDataBank, y: yDataBank, name: nameDataBank, category: categoryDataBank });
            setHealthData({ x: xDataHealth, y: yDataHealth, name: nameDataHealth, category: categoryDataHealth });
        } catch (error) {
            console.error('Error fetching company data:', error);
        }
    };

    const handlePlotClick = (event: any) => {
        if (event.points.length > 0) {
            const index = event.points[0].pointNumber;
            setSelectedIndex(index);
            if (onCompanyChange) {
                console.log(index);
                onCompanyChange(index + 1 + (selectedCategory === 'tech' ?  0 : selectedCategory === 'bank' ? 10 : 5) );  // companyId = index+1
            }
        }
    };

    const dataTech = {
        x: techData.x,
        y: techData.y,
        text: techData.name,   // shows company names on hover
        mode: 'markers' as const,
        type: 'scatter' as const,
        marker: { color: 'green' },
        name: 'Tech Companies',
    };

    const dataBank = {
        x: bankData.x,
        y: bankData.y,
        text: bankData.name,   // shows company names on hover
        mode: 'markers' as const,
        type: 'scatter' as const,
        marker: { color: 'orange' },
        name: 'Bank Companies',
    };

    const dataHealth = {
        x: healthData.x,
        y: healthData.y,
        text: healthData.name,   // shows company names on hover
        mode: 'markers' as const,
        type: 'scatter' as const,
        marker: { color: 'purple' },
        name: 'Health Companies',
    };

    const data = [dataTech, dataBank, dataHealth];

    const layout = {
        title: {text:`Overview of ${selectedCategory} Companies`},
        height: window.innerHeight * 0.9,
        xaxis: { title: {text:'Founding Year'} },
        yaxis: { title: {text:'Employees'} },
        showlegend: true
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
                    onClick={handlePlotClick}
                />

            </CardContent>
        </Card>
    );
}

export default ScatterPlot;


