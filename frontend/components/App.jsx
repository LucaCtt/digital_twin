import { useState, useEffect } from "react";
import { Flowbite } from "flowbite-react";
import ErrorBanner from "./ErrorBanner";
import Title from "./Title";
import AppliancesList from "./AppliancesList";
import RoutinesList from "./RoutinesList";

const App = () => {
  const [appliances, setAppliances] = useState([]);
  const [routines, setRoutines] = useState([]);
  const [showErrorBanner, setShowErrorBanner] = useState(false);

  useEffect(() => {
    const appliancesReq = fetch("/api/appliances")
      .then((response) => response.json())
      .then((data) => {
        setAppliances(data);
      })

    const routinesReq = fetch("/api/routines")
      .then((response) => response.json())
      .then((data) => {
        setRoutines(data);
      })

    Promise.all([appliancesReq, routinesReq])
    .then(() => setShowErrorBanner(false))
      .catch(() => setShowErrorBanner(true));

  });

  return (
    <Flowbite>
      <div className="flex flex-col justify-between gap-8">
        <ErrorBanner visible={showErrorBanner} />
        <Title />
        <AppliancesList appliances={appliances} />
        <RoutinesList routines={routines} />
      </div>
    </Flowbite>
  );
};

export default App;
