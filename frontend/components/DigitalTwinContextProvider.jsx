import { createContext, useState, useEffect } from "react";

import * as noConflict from "../test_routines/no_conflict.json";
import * as maxPowerExceeded from "../test_routines/max_power_exceeded.json";
import * as conflictingModes from "../test_routines/conflicting_modes.json";

const rawSimulatedRoutines = [noConflict, maxPowerExceeded, conflictingModes];

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
    consumptionsPerHour: [],
  },
  hasError: false,
  simulate: () => {},
  resetSimulationStatus: () => {},
});

const apiFetch = async (path, method = "GET", body = null) => {
  const response = await fetch(`${import.meta.env.DT_BACKEND_URL}${path}`, {
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
    consumptionsPerHour: [],
  });

  const hourDates = Array.from({ length: 24 }, (_, hour) => {
    const dateAtHour = new Date(timeNow);
    dateAtHour.setHours(hour, 0);
    return dateAtHour.toISOString();
  });
  const datesQueryParam = hourDates.map((date) => `when=${date}`).join("&");

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
    const { value: consumptionsPerHour } = await apiFetch(
      `/consumption/total/?${datesQueryParam}`,
    );
    setConsumptionsPerHour(consumptionsPerHour.map((c) => c / 1000));
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
    const { errors, recommendations } = await apiFetch(
      "/simulate",
      "POST",
      routine,
    );

    const { value: consumptionsPerHour } = await apiFetch(
      `/simulate/consumption/total/?${datesQueryParam}`,
      "POST",
      routine,
    );

    setSimulationStatus({
      isSimulating: false,
      errors,
      recommendations,
      consumptionsPerHour: consumptionsPerHour.map((c) => c / 1000),
    });
  };

  const resetSimulationStatus = () => {
    setSimulationStatus({
      isSimulating: false,
      errors: [],
      recommendations: [],
      consumptionsPerHour: [],
    });
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
        resetSimulationStatus,
      }}
    >
      {children}
    </DigitalTwinContext.Provider>
  );
};

export default DigitalTwinContextProvider;
