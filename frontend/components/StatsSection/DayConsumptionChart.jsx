import ConsumptionChart from "../ConsumptionChart";

const DayConsumptionChart = ({ data, className }) => {
  const series = [
    {
      name: "Total consumption (kW)",
      data,
    },
  ];

  return (
    <div
      className={`flex max-w-4xl flex-col justify-between rounded-lg bg-gray-100 p-8 dark:bg-gray-800 ${className}`}
    >
      <h2>Predicted Consumptions for Today</h2>
      <ConsumptionChart series={series} className={className} />
    </div>
  );
};

export default DayConsumptionChart;
