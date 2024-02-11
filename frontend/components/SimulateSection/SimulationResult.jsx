import { Alert } from "flowbite-react";
import { MdInfo, MdError } from "react-icons/md";
import ConsumptionChart from "../ConsumptionChart";

const SimulationResult = ({ consumptionsPerHour, simulationStatus }) => {
  const series = [
    {
      name: "Consumption with only existing routines (kW)",
      data: consumptionsPerHour,
    },
    {
      name: "Consumption with simulated routine (kW)",
      data: simulationStatus.consumptionsPerHour,
    },
  ];

  if (simulationStatus.consumptionsPerHour?.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 rounded-lg bg-gray-200 dark:bg-gray-700">Results will be shown here</div>
    )
  }

  return (
    <div className="flex flex-col gap-8">
      <div className="w-full h-96">
        <ConsumptionChart series={series} className="w-full" />
      </div>
      {simulationStatus.errors.map((error, index) => (
        <Alert color="failure" icon={MdError} key={`e-${index}`}>
          <span className="font-medium">{error.message}</span>
        </Alert>
      ))}
      {simulationStatus.recommendations.map((recommendation, index) => (
        <Alert color="info" icon={MdInfo} key={`r-${index}`}>
          <span className="font-medium">{recommendation.message}</span>
        </Alert>
      ))}
    </div>
  );
};

export default SimulationResult;
