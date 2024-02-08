import { useState, useEffect, useMemo } from "react";
import { Flowbite } from "flowbite-react";
import ErrorBanner from "./ErrorBanner";
import TitleBar from "./TitleBar";
import AppliancesSection from "./AppliancesSection";
import RoutinesSection from "./RoutinesSection";
import SimulateSection from "./SimulateSection";
import StatsSection from "./StatsSection";

import * as noConflict from "../test-routines/no_conflict.json";

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
    new Array(24).fill(0),
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
      .then((response) => response.json())
      .catch((err) => {
        setShowErrorBanner(true);
        console.error(err);
        throw err;
      });

  const fetchData = () => {
    setTimeNow(new Date().toISOString());

    apiFetch(`/consumption/total/${timeNow}`).then((data) =>
      setConsumptionNow(data.value),
    );

    apiFetch("/appliance").then((data) => {
      setAppliances(
        data.value.sort((a, b) => a.device.localeCompare(b.device)),
      );
    });

    apiFetch("/routine").then((data) => {
      setRoutines(data.value.sort((a, b) => a.when.localeCompare(b.when)));
    });

    const hourPromises = Array.from({ length: 24 }, (_, hour) => {
      const dateAtHour = new Date(timeNow);
      dateAtHour.setHours(hour, 0);

      apiFetch(`/consumption/total/${dateAtHour}`).then((data) => data.value);
    });
    Promise.all(hourPromises).then((result) => setConsumptionsPerHour(result));
  };

  useEffect(() => {
    apiFetch(`/consumption/${timeNow}`).then((data) => {
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
        <TitleBar />
        <StatsSection
          consumptionNow={consumptionNow}
          mostConsumingAppliances={mostConsumingAppliances}
          consumptionsPerHour={consumptionsPerHour}
        />
        <SimulateSection />
        <AppliancesSection appliances={appliances} />
        <RoutinesSection routines={routines} />
      </div>
    </Flowbite>
  );
};

export default App;
