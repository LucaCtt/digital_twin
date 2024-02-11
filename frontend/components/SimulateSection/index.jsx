import { useContext } from "react";
import { Button, Tabs } from "flowbite-react";
import { DigitalTwinContext } from "../DigitalTwinContextProvider";
import SimulationResult from "./SimulationResult";
import SimulatedRoutineDetails from "./SimulatedRoutineDetails";

const SimulateSection = () => {
  const {
    consumptionsPerHour,
    simulatedRoutines,
    simulationStatus,
    simulate,
    resetSimulationStatus,
  } = useContext(DigitalTwinContext);

  return (
    <div className="flex flex-col justify-between rounded-lg bg-gray-100 p-8 dark:bg-gray-800">
      <h2>Simulate Routines</h2>

      <Tabs
        aria-label="Tabs with underline"
        style="underline"
        onActiveTabChange={() => resetSimulationStatus()}
      >
        {simulatedRoutines.map((routine) => (
          <Tabs.Item title={routine.name} key={routine.id}>
            <div className="flex flex-col gap-8">
              <SimulatedRoutineDetails routine={routine} />
              <Button
                color="green"
                className="rounded-lg bg-green-500 text-white focus:outline-none focus:ring-4 focus:ring-green-300 enabled:hover:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800 dark:enabled:bg-green-600"
                onClick={() => simulate(routine)}
                isProcessing={simulationStatus.isSimulating}
              >
                Simulate routine addition
              </Button>
              <SimulationResult
                consumptionsPerHour={consumptionsPerHour}
                simulationStatus={simulationStatus}
              />
            </div>
          </Tabs.Item>
        ))}
      </Tabs>
    </div>
  );
};

export default SimulateSection;
