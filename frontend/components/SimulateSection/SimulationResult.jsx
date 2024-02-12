import { Alert } from "flowbite-react";
import { MdInfo, MdError } from "react-icons/md";
import ConsumptionChart from "../ConsumptionChart";

const format_recommendation = ({ type, context }) => {
  switch (type) {
    case "DISABLE_ROUTINE":
      return (
        <span>
          Disable routine <i>{context["routine"]["name"]}</i>
        </span>
      );
    case "CHANGE_ROUTINE_START_TIME":
      const hour = new Date(context["when"]).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });

      return (
        <span>
          Start the routine at {hour} to save {context["savings"].toFixed(4)}€
        </span>
      );
  }
};

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

  if (!simulationStatus.isSimulationDone) {
    return (
      <div className="flex h-96 items-center justify-center rounded-lg bg-gray-200 dark:bg-gray-700">
        Results will be shown here
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8">
      {!simulationStatus.error && (
        <div className="h-96 w-full">
          <ConsumptionChart series={series} className="w-full" />
        </div>
      )}

      <div className="flex flex-col gap-4">
        {simulationStatus.error && (
          <Alert color="failure" icon={MdError}>
            <span className="font-medium">
              {simulationStatus.error.message}
            </span>
          </Alert>
        )}
        {simulationStatus.recommendations?.map((recommendation, index) => (
          <Alert color="info" icon={MdInfo} key={`r-${index}`}>
            {format_recommendation(recommendation)}
          </Alert>
        ))}
      </div>
    </div>
  );
};

export default SimulationResult;
