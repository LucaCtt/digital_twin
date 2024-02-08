import ConsumptionNow from "./ConsumptionNow";
import MostConsumingAppliances from "./MostConsumingAppliances";
import DayConsumptionChart from "./DayConsumptionChart";

const StatsSection = ({
  consumptionNow,
  mostConsumingAppliances,
  consumptionsPerHour,
}) => {
  return (
    <div className="flex flex-col justify-between gap-8 lg:flex-row">
      <div className="flex flex-col justify-between gap-8 md:flex-row lg:flex-col">
        <ConsumptionNow
          consumption={consumptionNow}
          className="h-full w-full"
        />
        <MostConsumingAppliances
          appliancesConsumption={mostConsumingAppliances}
          className="h-full w-full"
        />
      </div>
      <DayConsumptionChart data={consumptionsPerHour} className="w-full" />
    </div>
  );
};

export default StatsSection;
