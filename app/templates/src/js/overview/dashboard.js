import {ArcElement, Chart, DoughnutController, Legend, Tooltip} from "chart.js";
import ChartDataLabels from 'chartjs-plugin-datalabels';


class Dashboard {
    constructor(env, rootElement) {
        this.env = env;
        this.rootElement = rootElement;
        Chart.register(DoughnutController, ArcElement, Legend, ChartDataLabels, Tooltip);
        Chart.defaults.font.size = 14;
    }

    updateRetrievalByHarvester(fakeRetrievalByHarvesterData) {
        const chartJsData = {
            labels: Object.keys(fakeRetrievalByHarvesterData),
            data: Object.values(fakeRetrievalByHarvesterData)
        }
        this.updateRetrievalByHarvesterChart(chartJsData);
    }

    updateRetrievalByHarvesterChart(chartJsData) {

        const ctx = this.rootElement.querySelector("#references-by-harvester-chart");
        new Chart(ctx, {
            type: 'doughnut',
            responsive: true,
            data: {
                labels: chartJsData.labels,
                datasets: [{
                    data: chartJsData.data,
                    backgroundColor: [
                        'rgb(255, 99, 132)',
                        'rgb(54, 162, 235)',
                        'rgb(255, 205, 86)',
                        'rgb(75, 192, 192)',
                        'rgb(153, 102, 255)',
                    ],
                    hoverOffset: 50
                }],
            },
            options: {
                layout: {
                    padding: 20
                },
                tooltips: {
                    enabled: true
                },

                plugins: {
                    tooltip: {
                        enabled: true,
                        backgroundColor: "#042a0b",
                        titleColor: "#fff",
                        bodyColor: "#fff",
                        titleFont: {weight: 'bold'},
                        padding: 10,
                        cornerRadius: 10,
                        borderColor: "#fff",
                        borderWidth: "2",
                        xAlign: "left",
                        callbacks: {
                            label: function (tooltipData) {
                                const datapoints = tooltipData.dataset.data
                                const total = datapoints.reduce((total, datapoint) => total + datapoint, 0)
                                const percentage = tooltipData.raw / total * 100
                                return percentage.toFixed(2) + "%";
                            },
                        },
                    },
                    legend: {
                        display: true,
                        labels: {
                            color: 'rgb(255, 99, 132)',
                            font: {
                                size: 18,
                                weight: 'bold'
                            }
                        }
                    },
                    datalabels: {
                        formatter: (value, ctx) => {
                            // # display with spaces
                            return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
                        },
                    }
                },
            },
        });
    }
}


export default Dashboard;