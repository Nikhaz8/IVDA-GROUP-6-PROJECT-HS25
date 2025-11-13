import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import Plot from 'react-plotly.js';

interface BarChartProps {
    selectedCompany: number;
    onCompanyChange?: (companyId: number) => void;
}

function BarChart({ selectedCompany, onCompanyChange }: BarChartProps) {

    const [techData, setTechData] = useState({
        x: [] as string[],
        y: [] as number[],
        id: [] as number[],
        category: [] as string[]
    });

    const [bankData, setBankData] = useState({
        x: [] as string[],
        y: [] as number[],
        id: [] as number[],
        category: [] as string[]
    });

    const [healthData, setHealthData] = useState({
        x: [] as string[],
        y: [] as number[],
        id: [] as number[],
        category: [] as string[]
    });

    const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

    useEffect(() => {
        fetchData();
    }, [selectedCompany]); // Re-fetch when category changes

    const fetchData = async () => {
        try {
            // req URL to retrieve companies from backend with category filter
            const reqUrl = `http://127.0.0.1:5000/companies?category=${selectedCompany < 6? 'tech' : selectedCompany > 10 ? 'bank' : 'health'}`;
            console.log("ReqURL " + reqUrl);

            // await response and data
            const response = await fetch(reqUrl);
            const responseData = await response.json();

            const xDataTech: string[] = [];
            const yDataTech: number[] = [];
            const idDataTech: number[] = [];
            const categoryDataTech: string[] = [];

            const xDataBank: string[] = [];
            const yDataBank: number[] = [];
            const idDataBank: number[] = [];
            const categoryDataBank: string[] = [];

            const xDataHealth: string[] = [];
            const yDataHealth: number[] = [];
            const idDataHealth: number[] = [];
            const categoryDataHealth: string[] = [];

            responseData.forEach((company: any) => {
                if (company.category === 'tech') {
                    xDataTech.push(company.name);
                    yDataTech.push(company.employees);
                    idDataTech.push(company.id);
                    categoryDataTech.push(company.category);
                } else if (company.category === 'bank') {
                    xDataBank.push(company.name);
                    yDataBank.push(company.employees);
                    idDataBank.push(company.id);
                    categoryDataBank.push(company.category);
                } else if (company.category === 'health') {
                    xDataHealth.push(company.name);
                    yDataHealth.push(company.employees);
                    idDataHealth.push(company.id);
                    categoryDataHealth.push(company.category);
                }
            });
            setTechData({ x: xDataTech, y: yDataTech, id: idDataTech, category: categoryDataTech });
            setBankData({ x: xDataBank, y: yDataBank, id: idDataBank, category: categoryDataBank });
            setHealthData({ x: xDataHealth, y: yDataHealth, id: idDataHealth, category: categoryDataHealth });
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
                onCompanyChange(index + 1 + (selectedCompany < 6 ?  0 : selectedCompany > 10 ? 10 : 5) );  // companyId = index+1
            }
        }
    };

    const dataTech = [{
        x: techData.x,
        y: techData.y,
        text: techData.x,   // shows company names on hover
        mode: 'markers' as const,
        type: 'bar' as const,
        marker: { color: techData.id.map((id) =>
                id === selectedCompany ? 'black' : 'green')},
        name: 'Tech Companies',
    }];

    const dataBank = [{
        x: bankData.x,
        y: bankData.y,
        text: bankData.x,   // shows company names on hover
        mode: 'markers' as const,
        type: 'bar' as const,
        marker: { color: bankData.id.map((id) =>
                id === selectedCompany ? 'black' : 'orange')},
        name: 'Bank Companies',
    }];

    const dataHealth = [{
        x: healthData.x,
        y: healthData.y,
        text: healthData.x,   // shows company names on hover
        mode: 'markers' as const,
        type: 'bar' as const,
        marker: { color: healthData.id.map((id) =>
                id === selectedCompany ? 'black' : 'purple')},
        name: 'Health Companies',
    }];

    const data = selectedCompany < 6 ? dataTech : selectedCompany > 10 ? dataBank : dataHealth;

    const layout = {
        title: {text:`Overview of 5 Companies`},
        height: window.innerHeight * 0.9,
        xaxis: { title: {text:'Company'} },
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

export default BarChart;