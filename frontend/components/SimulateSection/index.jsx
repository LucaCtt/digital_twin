import { Tabs } from "flowbite-react";
import SimulatedRoutineDetails from "./SimulatedRoutineDetails";
import SimulationResult from "./SimulationResult";

const SimulationBox = ({ routine, onSimulate, result }) => {
  <div className="flex hidden flex-col md:flex-row gap-8 p-4">
    <div className="flex w-full flex-col justify-between gap-8">
      <SimulatedRoutineDetails routine={routine} />
      <Button
        class="me-2 w-full rounded-lg bg-green-500 px-5 py-2.5 text-sm text-white hover:bg-green-600 focus:outline-none focus:ring-4 focus:ring-green-300 dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800"
        onCLick={onSimulate}
      >
        Simulate routine addition
      </Button>
    </div>
    <SimulationResult result={result} />
  </div>;
};

const SimulateSection = ({ routines, onSimulate, result }) => {
  return (
    <div className="flex flex-col justify-between rounded-lg bg-gray-100 p-8 dark:bg-gray-800">
      <h2>Simulate Routines</h2>
      <Tabs aria-label="Tabs with underline" style="underline">
        {routines?.map((routine) => (
          <Tabs.Item title={routine.name} key={routine.id}>
            <SimulationBox routine={routine} onSimulate={() => onSimulate(routine)} result={result}/>
          </Tabs.Item>
        ))}
      </Tabs>
    </div>
  );
};

export default SimulateSection;
