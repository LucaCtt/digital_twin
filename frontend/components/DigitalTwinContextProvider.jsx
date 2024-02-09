import { createContext, useState, useEffect } from "react";

import * as noConflict from "../test-routines/no_conflict.json";
const rawSimulatedRoutines = [noConflict];

export const DigitalTwinContext = createContext({
  consumptionNow: 0,
  consumptionsPerHour: new Array(24).fill(0),
  mostConsumingAppliances: [],
  appliances: [],
  routines: [],
  simulatedRoutines: [],
  simulationStatus: {
    isSimulating: false,
    errors: [],
    recommendations: [],
  },
  hasError: false,
  simulate: () => {},
});

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

const DigitalTwinContextProvider = ({ children }) => {
  const [timeNow, setTimeNow] = useState(new Date().toISOString());
  const [hasError, setHasError] = useState(false);
  const [consumptionNow, setConsumptionNow] = useState(0);
  const [consumptionsPerHour, setConsumptionsPerHour] = useState(
    new Array(24).fill(0),
  );
  const [mostConsumingAppliances, setMostConsumingAppliances] = useState([]);
  const [appliances, setAppliances] = useState([]);
  const [routines, setRoutines] = useState([]);
  const [simulatedRoutines, setSimulatedRoutines] = useState([]);
  const [simulationStatus, setSimulationStatus] = useState({
    isSimulating: false,
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

  const fetchRoutines = async () => {
    const { value: routine } = await apiFetch("/routine");
    const sortedRoutines = routine.sort((a, b) => a.when.localeCompare(b.when));
    setRoutines(sortedRoutines);
  };

  const fetchAllData = async () => {
    setTimeNow(new Date().toISOString());

    try {
      await Promise.all([
        fetchTotalConsumption(),
        fetchAppliances(),
        fetchRoutines(),
        fetchConsumptionsPerHour(),
      ]);
      setHasError(false);
    } catch (err) {
      setHasError(true);
      console.error(err);
    }
  };

  const simulate = async (routine) => {
    setSimulationStatus({
      isSimulating: true,
      errors: [],
      recommendations: [],
    });

    const { errors, recommendations } = await apiFetch(
      "/simulate",
      "POST",
      routine,
    );

    setSimulationResult({ isSimulating: false, errors, recommendations });
  };

  useEffect(() => {
    // Fetch the data on component mount
    fetchAllData();

    // Then fetch the data every 5 seconds
    const intervalId = setInterval(fetchAllData, 10 * 1000);

    // Clear the interval when the component is unmounted
    return () => clearInterval(intervalId);
  }, []);

  return (
    <DigitalTwinContext.Provider
      value={{
        consumptionNow,
        consumptionsPerHour,
        mostConsumingAppliances,
        appliances,
        routines,
        simulatedRoutines,
        simulationStatus,
        hasError,
        simulate,
      }}
    >
      {children}
    </DigitalTwinContext.Provider>
  );
};

export default DigitalTwinContextProvider;