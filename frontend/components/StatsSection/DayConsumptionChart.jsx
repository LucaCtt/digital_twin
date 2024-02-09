import Chart from "react-apexcharts";

const DayConsumptionChart = ({ data, className }) => {
  const options = {
    chart: {
      id: "day-consumption-chart",
      toolbar: {
        show: false,
      },
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      width: 4,
    },
    xaxis: {
      // List of hours from midnight to 11 PM
      title: {
        text: "Hour",
        style: {
          cssClass: "font-normal mb-2 text-md fill-gray-600 dark:fill-gray-400",
        },
      },
      labels: {
        rotateAlways: true,
        style: {
          cssClass: "font-normal fill-gray-600 dark:fill-gray-400",
        },
      },
      categories: Array.from({ length: 24 }, (_, i) => {
        const date = new Date();
        date.setHours(i, 0, 0);
        return date.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        });
      }),
    },
    yaxis: {
      title: {
        text: "Total Energy Consumption (KW)",
        style: {
          cssClass: "font-normal text-md fill-gray-600 dark:fill-gray-400",
        },
      },
      labels: {
        style: {
          cssClass: "font-normal fill-gray-600 dark:fill-gray-400",
        },
      },
      min: 0,
      max: 3,
      decimalsInFloat: 1,
      stepSize: 0.5,
    },
    colors: ["#0E9F6E"],
  };

  const series = [
    {
      name: "Total consumption (kW)",
      data: data.map((c) => c / 1000),
    },
  ];

  return (
    <div
      className={`flex max-w-4xl flex-col justify-between rounded-lg bg-gray-100 p-8 dark:bg-gray-800 ${className}`}
    >
      <h2>Predicted Consumptions for Today</h2>
      <Chart
        options={options}
        series={series}
        type="area"
        height="100%"
        width="100%"
      />
    </div>
  );
};

export default DayConsumptionChart;
