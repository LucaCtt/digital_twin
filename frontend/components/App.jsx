import { Flowbite } from "flowbite-react";

import DigitalTwinContextProvider from "./DigitalTwinContextProvider";
import ErrorBanner from "./ErrorBanner";
import TitleBar from "./TitleBar";
import AppliancesSection from "./AppliancesSection";
import RoutinesSection from "./RoutinesSection";
import SimulateSection from "./SimulateSection";
import StatsSection from "./StatsSection";

const flowbiteTheme = {
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

const App = () => (
  <DigitalTwinContextProvider>
    <Flowbite theme={{ theme: flowbiteTheme }}>
      <div className="flex flex-col justify-between gap-8">
        <ErrorBanner />
        <TitleBar />
        <StatsSection />
        <SimulateSection />
        <AppliancesSection />
        <RoutinesSection />
      </div>
    </Flowbite>
  </DigitalTwinContextProvider>
);

export default App;
