import { useState, useEffect, useMemo } from "react";
import { Flowbite } from "flowbite-react";
import ErrorBanner from "./ErrorBanner";
import TitleBar from "./TitleBar";
import AppliancesSection from "./AppliancesSection";
import RoutinesSection from "./RoutinesSection";
import SimulateSection from "./SimulateSection";
import StatsSection from "./StatsSection";

import * as noConflict from "../test-routines/no_conflict.json";

const rawSimulatedRoutines = [noConflict];

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

const apiFetch = async (path, method = "GET", body = null) => {
  const response = await fetch(`${process.env.BACKEND_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : null,
  });
  const data = await response.json();
  return data;
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
  const [simulatedRoutines, setSimulatedRoutines] = useState([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState({
    errors: [],
    recommendations: [],
  });

  const fetchTotalConsumption = async () => {
    const totalConsumption = (await apiFetch(`/consumption/total/${timeNow}`))
      .value;
    setConsumptionNow(totalConsumption);
  };

  const fetchAppliances = async () => {
    const { value: appliancesData } = await apiFetch("/appliance");
    const sortedAppliances = appliancesData.sort((a, b) =>
      a.device.localeCompare(b.device),
    );
    setAppliances(sortedAppliances);

    if (appliancesData.length === 0) return;

    const { value: mostConsumingRaw } = await apiFetch(
      `/consumption/${timeNow}`,
    );
    const mostConsuming = mostConsumingRaw
      .sort((a, b) => b.consumption - a.consumption)
      .slice(0, 3)
      .map(({ appliance_id, consumption }) => {
        const appliance = appliancesData.find(
          (appliance) => appliance.id === appliance_id,
        );
        return { appliance: appliance, consumption: consumption };
      });

    setMostConsumingAppliances(mostConsuming);

    const simulatedRoutines = rawSimulatedRoutines.map((routine) => {
      const simulatedActions = routine.actions.map((action) => {
        const appliance = appliancesData.find(
          (appliance) => appliance.id === action.appliance_id,
        );
        const mode = appliance.modes.find((mode) => mode.id === action.mode_id);
        return { ...action, mode, appliance, duration: action.duration / 60 };
      });
      return { ...routine, actions: simulatedActions };
    });
    setSimulatedRoutines(simulatedRoutines);
  };

  const fetchRoutines = async () => {
    const { value: routine } = await apiFetch("/routine");
    const sortedRoutines = routine.sort((a, b) => a.when.localeCompare(b.when));
    setRoutines(sortedRoutines);
  };

  const fetchConsumptionsPerHour = async () => {
    const dates = Array.from({ length: 24 }, (_, hour) => {
      const dateAtHour = new Date(timeNow);
      dateAtHour.setHours(hour, 0);
      return dateAtHour.toISOString();
    });
    const datesQueryParam = dates.map((date) => `when=${date}`).join("&");

    const { value: consumptionsPerHour } = await apiFetch(
      `/consumption/total/?${datesQueryParam}`,
    );
    setConsumptionsPerHour(consumptionsPerHour);
  };

  const fetchData = async () => {
    setTimeNow(new Date().toISOString());

    try {
      await Promise.all([
        fetchTotalConsumption(),
        fetchAppliances(),
        fetchRoutines(),
        fetchConsumptionsPerHour(),
      ]);
      setShowErrorBanner(false);
    } catch (err) {
      setShowErrorBanner(true);
      console.error(err);
    }
  };

  const simulate = async (routine) => {
    setIsSimulating(true);
    const { errors, recommendations } = await apiFetch(
      "/simulate",
      "POST",
      routine,
    );
    setSimulationResult({ errors, recommendations });
    setIsSimulating(false);
  };

  useEffect(() => {
    // Fetch the data on component mount
    fetchData();

    // Then fetch the data every 5 seconds
    const intervalId = setInterval(fetchData, 10 * 1000);

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
        <SimulateSection
          routines={simulatedRoutines}
          onSimulate={simulate}
          isSimulating={isSimulating}
          result={simulationResult}
        />
        <AppliancesSection appliances={appliances} />
        <RoutinesSection routines={routines} />
      </div>
    </Flowbite>
  );
};

export default App;
