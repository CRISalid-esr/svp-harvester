import {
    ArcElement,
    BarController, BarElement,
    CategoryScale,
    Chart,
    DoughnutController,
    Legend,
    LinearScale,
    Tooltip
} from "chart.js";
import ChartDataLabels from 'chartjs-plugin-datalabels';


class Dashboard {
    constructor(env, rootElement) {
        this.env = env;
        this.rootElement = rootElement;
        Chart.register(BarController, BarElement, DoughnutController, ArcElement, Legend, ChartDataLabels, Tooltip, CategoryScale, LinearScale);
        Chart.defaults.font.size = 14;
    }

    updateRetrievalByHarvester(data) {
        const chartJsData = {
            labels: Object.keys(data),
            data: Object.values(data)
        }
        this.updateRetrievalByHarvesterChart(chartJsData);
    }

    updateReferenceEventsByDayAndType(data) {
        const days_labels = Object.keys(data);
        const chartJsDatasets = this.convertToDatasets(data);
        this.updateReferenceEventsByDayAndTypeChart(chartJsDatasets, days_labels);

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

    updateReferenceEventsByDayAndTypeChart(chartJsData, day_labels) {
        const ctx = this.rootElement.querySelector("#reference-events-by-day-and-type");
        const myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: day_labels,
                datasets: chartJsData
            },
            options: {
                layout: {
                    padding: 50
                },
                scales: {
                    x: {
                        stacked: true
                    },
                    y: {
                        stacked: true
                    }
                },
                plugins: {
                    datalabels: {
                        display: 'auto',
                        formatter: function (value) {
                            if (value > 0) {
                                return value;
                            } else {
                                return null;
                            }
                        },
                    }
                }
            }
        });
    }

    convertToDatasets(data) {
        let result = [];
        const labelColors = {
            "created": "rgb(75, 192, 192)",
            "updated": "rgb(54, 162, 235)",
            "deleted": "rgb(255, 99, 132)",
            "unchanged": "rgb(255, 205, 86)"
        }
        for (const eventType in labelColors) {
            result.push({
                label: eventType,
                data: Array(Object.keys(data).length).fill(0),
                backgroundColor: labelColors[eventType]
            });
        }
        let dateCount = 0;
        for (let date in data) {
            let events = data[date];
            for (let eventType in events) {
                const foundLabelIndex = result.findIndex(item => item.label === eventType);
                if (foundLabelIndex !== -1) {
                    result[foundLabelIndex].data[dateCount] = events[eventType];
                }

            }
            dateCount++;
        }
        return result;
    }
}


export default Dashboard;