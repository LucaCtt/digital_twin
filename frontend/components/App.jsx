import { useState, useEffect } from "react";
import { Flowbite } from "flowbite-react";
import ErrorBanner from "./ErrorBanner";
import Title from "./Title";
import AppliancesList from "./AppliancesList";
import RoutinesList from "./RoutinesList";
import SimulateSection from "./SimulateSection";

const apiFetch = (path) => fetch(process.env.BACKEND_URL + path);

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
  const [appliances, setAppliances] = useState([]);
  const [routines, setRoutines] = useState([]);
  const [showErrorBanner, setShowErrorBanner] = useState(false);

  useEffect(() => {
    const appliancesReq = apiFetch("/appliance")
      .then((response) => response.json())
      .then((data) => {
        setAppliances(
          data.value.sort((a, b) => a.device.localeCompare(b.device)),
        );
      });

    const routinesReq = apiFetch("/routine")
      .then((response) => response.json())
      .then((data) => {
        setRoutines(data.value.sort((a, b) => a.when.localeCompare(b.when)));
      });

    Promise.all([appliancesReq, routinesReq])
      .then(() => setShowErrorBanner(false))
      .catch(() => setShowErrorBanner(true));
  }, []);

  return (
    <Flowbite theme={{ theme: customTheme }}>
      <div className="flex flex-col justify-between gap-8">
        <ErrorBanner visible={showErrorBanner} />
        <Title />
        <SimulateSection />
        <AppliancesList appliances={appliances} />
        <RoutinesList routines={routines} />
      </div>
    </Flowbite>
  );
};

export default App;
