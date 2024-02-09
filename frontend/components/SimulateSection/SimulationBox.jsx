import { Button } from "flowbite-react";
import SimulatedRoutineDetails from "./SimulatedRoutineDetails";
import SimulationResult from "./SimulationResult";

const SimulationBox = ({
  routine,
  onSimulate,
  isSimulating,
  errors,
  recommendations,
}) => {
  return (
    <div className="flex flex-col gap-8 pt-4 lg:flex-row">
      <div className="flex w-full flex-col justify-between gap-8">
        <SimulatedRoutineDetails routine={routine} />
        <Button
          color="green"
          className="rounded-lg bg-green-500 text-white focus:outline-none focus:ring-4 focus:ring-green-300 enabled:hover:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800 dark:enabled:bg-green-600"
          onClick={onSimulate}
          isProcessing={isSimulating}
        >
          Simulate routine addition
        </Button>
      </div>
      <SimulationResult
        recommendations={recommendations}
        errors={errors}
        className="w-full"
      />
    </div>
  );
};

export default SimulationBox;
