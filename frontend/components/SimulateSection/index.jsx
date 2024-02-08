import { Tabs } from "flowbite-react";
import SimulationBox from "./SimulationBox";

const SimulateSection = ({ routines, onSimulate, isSimulating, result }) => {
  return (
    <div className="flex flex-col justify-between rounded-lg bg-gray-100 p-8 dark:bg-gray-800">
      <h2>Simulate Routines</h2>
      <Tabs aria-label="Tabs with underline" style="underline">
        {routines.map((routine) => (
          <Tabs.Item title={routine.name} key={routine.id}>
            <SimulationBox
              routine={routine}
              onSimulate={() => onSimulate(routine)}
              isSimulating={isSimulating}
              result={result}
            />
          </Tabs.Item>
        ))}
      </Tabs>
    </div>
  );
};

export default SimulateSection;
