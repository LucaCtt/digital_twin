import { useContext } from "react";
import { Tabs } from "flowbite-react";
import SimulationBox from "./SimulationBox";
import { DigitalTwinContext } from "../DigitalTwinContextProvider";

const SimulateSection = () => {
  const { simulatedRoutines, simulationStatus, simulate } =
    useContext(DigitalTwinContext);

  return (
    <div className="flex flex-col justify-between rounded-lg bg-gray-100 p-8 dark:bg-gray-800">
      <h2>Simulate Routines</h2>
      <Tabs aria-label="Tabs with underline" style="underline">
        {simulatedRoutines.map((routine) => (
          <Tabs.Item title={routine.name} key={routine.id}>
            <SimulationBox
              routine={routine}
              onSimulate={() => simulate(routine)}
              isSimulating={simulationStatus.isSimulating}
              errors={simulationStatus.errors}
              recommendations={simulationStatus.recommendations}
            />
          </Tabs.Item>
        ))}
      </Tabs>
    </div>
  );
};

export default SimulateSection;
