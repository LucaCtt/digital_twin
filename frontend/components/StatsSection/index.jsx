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
      <div className="flex flex-col justify-between gap-8 md:flex-row lg:flex-col flex-1" >
        <ConsumptionNow
          consumption={consumptionNow}
          className="flex-1"
        />
        <MostConsumingAppliances
          appliancesConsumption={mostConsumingAppliances}
          className="flex-1"
        />
      </div>
      <DayConsumptionChart data={consumptionsPerHour} className="w-full min-h-96" />
    </div>
  );
};

export default StatsSection;
