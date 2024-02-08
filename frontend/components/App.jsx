import { useState, useEffect, useMemo } from "react";
import { Flowbite } from "flowbite-react";
import ErrorBanner from "./ErrorBanner";
import Title from "./Title";
import AppliancesList from "./AppliancesList";
import RoutinesList from "./RoutinesList";
import SimulateSection from "./SimulateSection";
import ConsumptionNow from "./ConsumptionNow";
import MostConsumingAppliances from "./MostConsumingAppliances";
import DayConsumptionChart from "./DayConsumptionChart";

const customTheme = {
  button: {
    size: {
      xs: "text-xs px-1 py-1",
      sm: "text-sm px-1.5 py-1.5",
      md: "text-sm px-2 py-2",
      lg: "text-base px-2.5 py-2.5",
      xl: "text-base px-4 py-3",
    },
  },
  tabs: {
    tablist: {
      tabitem: {
        base: "flex items-center justify-center p-4 rounded-t-lg text-md font-medium first:ml-0 disabled:cursor-not-allowed disabled:text-gray-400 disabled:dark:text-gray-500 focus:ring-4 focus:ring-green-200 focus:outline-none",
        styles: {
          underline: {
            active: {
              on: "text-green-600 rounded-t-lg border-b-2 border-green-600 active dark:text-green-500 dark:border-green-500",
            },
          },
        },
      },
    },
  },
};

const App = () => {
  const [timeNow, setTimeNow] = useState(new Date().toISOString());
  const [consumptionNow, setConsumptionNow] = useState(0);
  const [consumptionsPerHour, setConsumptionsPerHour] = useState(
    Array.from({ length: 24 }, (_, i) => 0),
  );
  const [mostConsumingAppliances, setMostConsumingAppliances] = useState([]);
  const [appliances, setAppliances] = useState([]);
  const [routines, setRoutines] = useState([]);
  const [showErrorBanner, setShowErrorBanner] = useState(false);

  const apiFetch = (path) =>
    fetch(`${process.env.BACKEND_URL}${path}`)
      .then((response) => {
        setShowErrorBanner(false);
        return response;
      })
      .catch((err) => {
        setShowErrorBanner(true);
        console.error(err);
        throw err;
      });

  const fetchData = () => {
    setTimeNow(new Date().toISOString());

    apiFetch(`/consumption/total/${timeNow}`)
      .then((response) => response.json())
      .then((data) => setConsumptionNow(data.value));

    apiFetch("/appliance")
      .then((response) => response.json())
      .then((data) => {
        setAppliances(
          data.value.sort((a, b) => a.device.localeCompare(b.device)),
        );
      });

    apiFetch("/routine")
      .then((response) => response.json())
      .then((data) => {
        setRoutines(data.value.sort((a, b) => a.when.localeCompare(b.when)));
      });

    const tempConsumptionsPerHour = Array.from({ length: 24 }, (_, i) => 0);
    const promises = [];
    for (let hour = 0; hour < 24; hour++) {
      const timeAtHour = new Date(timeNow).setHours(hour);
      promises.push(
        apiFetch(`/consumption/total/${timeAtHour}`)
          .then((response) => response.json())
          .then((data) => {
            tempConsumptionsPerHour[hour] = data.value;
          }),
      );
    }
    Promise.all(promises).then(() =>
      setConsumptionsPerHour(tempConsumptionsPerHour),
    );
  };

  useEffect(() => {
    if (appliances.length === 0) return;

    apiFetch(`/consumption/${timeNow}`)
      .then((response) => response.json())
      .then((data) => {
        const mostConsuming = data.value
          .sort((a, b) => b.consumption - a.consumption)
          .slice(0, 3)
          .map(({ appliance_id, consumption }) => {
            const appliance = appliances.find(
              (appliance) => appliance.id === appliance_id,
            );
            return { appliance: appliance, consumption: consumption };
          });

        setMostConsumingAppliances(mostConsuming);
      });
  }, [appliances]);

  useEffect(() => {
    // Fetch the data on component mount
    fetchData();

    // Then fetch the data every 5 seconds
    const intervalId = setInterval(fetchData, 5000);

    // Clear the interval when the component is unmounted
    return () => clearInterval(intervalId);
  }, []);

  return (
    <Flowbite theme={{ theme: customTheme }}>
      <div className="flex flex-col justify-between gap-8">
        <ErrorBanner visible={showErrorBanner} />
        <Title />
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
        <SimulateSection />
        <AppliancesList appliances={appliances} />
        <RoutinesList routines={routines} />
      </div>
    </Flowbite>
  );
};

export default App;
