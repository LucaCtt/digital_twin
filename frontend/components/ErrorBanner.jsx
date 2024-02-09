import { useContext } from "react";
import { Banner } from "flowbite-react";
import { MdError } from "react-icons/md";
import { DigitalTwinContext } from "./DigitalTwinContextProvider";

const ErrorBanner = () => {
  const { hasError } = useContext(DigitalTwinContext);

  return (
    <Banner>
      <div
        className={`fixed start-0 top-0 z-50 flex w-full bg-red-200 p-2 text-red-900 dark:bg-red-900 dark:text-white ${!hasError && "hidden"}`}
      >
        <p className="mx-auto flex items-center gap-2 text-sm font-normal">
          <MdError className="h-6 w-6" />
          <span>Could not fetch API data. Please try again later.</span>
        </p>
      </div>
    </Banner>
  );
};

export default ErrorBanner;
