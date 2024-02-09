import { useContext } from "react";
import ConsumptionNow from "./ConsumptionNow";
import MostConsumingAppliances from "./MostConsumingAppliances";
import DayConsumptionChart from "./DayConsumptionChart";
import { DigitalTwinContext } from "../DigitalTwinContextProvider";

const StatsSection = () => {
  const { consumptionNow, mostConsumingAppliances, consumptionsPerHour } =
    useContext(DigitalTwinContext);

  return (
    <div className="flex flex-col justify-between gap-8 lg:flex-row">
      <div className="flex flex-1 flex-col justify-between gap-8 md:flex-row lg:flex-col">
        <ConsumptionNow consumption={consumptionNow} className="flex-1" />
        <MostConsumingAppliances
          appliancesConsumption={mostConsumingAppliances}
          className="flex-1"
        />
      </div>
      <DayConsumptionChart
        data={consumptionsPerHour}
        className="min-h-96 w-full"
      />
    </div>
  );
};

export default StatsSection;
