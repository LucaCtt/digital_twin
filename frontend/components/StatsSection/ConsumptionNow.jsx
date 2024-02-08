import { useEffect, useState } from "react";

const ConsumptionNow = ({ consumption, className }) => {
  const [colorClass, setColorClass] = useState("text-green-500");

  useEffect(() => {
    setColorClass(
      consumption <= 1500
        ? "text-green-500"
        : consumption <= 2500
          ? "text-yellow-500"
          : "text-red-500",
    );
  }, [consumption]);

  return (
    <div
      className={`flex max-w-sm flex-col justify-between rounded-lg bg-gray-100 p-8 dark:bg-gray-800 ${colorClass} ${className}`}
    >
      <h2>Total Consumption Now</h2>
      <div className="flex h-full items-center justify-center">
        <span className="text-4xl font-bold">{consumption / 1000} kW</span>
      </div>
    </div>
  );
};

export default ConsumptionNow;
