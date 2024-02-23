import { Alert } from "flowbite-react";
import { MdInfo, MdError, MdPaid } from "react-icons/md";
import ConsumptionChart from "../ConsumptionChart";

const DisableRoutinesRecommendation = ({ routines }) => (
  <Alert color="info" icon={MdInfo}>
    Disable one of the following routines:{" "}
    <i>{routines.map((r) => r.name).join(", ")}</i>
  </Alert>
);

const ChangeRoutineStartTimeRecommendation = ({ when, savings }) => {
  const hour = new Date(when).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <Alert color="success" icon={MdPaid}>
      Starting the routine at {hour} can save {(savings * 30).toFixed(2)}€ over
      a month
    </Alert>
  );
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

  const disableRoutineRecommendations = simulationStatus.recommendations.filter(
    (s) => s.type === "DISABLE_ROUTINE",
  );
  const changeRoutineStartTimeRecommendations =
    simulationStatus.recommendations.filter(
      (s) => s.type === "CHANGE_ROUTINE_START_TIME",
    );

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
        {disableRoutineRecommendations.length > 0 && (
          <DisableRoutinesRecommendation
            routines={disableRoutineRecommendations.map(
              (r) => r.context.routine,
            )}
          />
        )}
        {changeRoutineStartTimeRecommendations.length > 0 &&
          changeRoutineStartTimeRecommendations.map((r) => (
            <ChangeRoutineStartTimeRecommendation
              when={r.context.when}
              savings={r.context.savings}
              key={r.context.when}
            />
          ))}
      </div>
    </div>
  );
};

export default SimulationResult;
