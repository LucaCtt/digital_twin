import { Banner } from "flowbite-react";


const ErrorIcon = () => {
  return (
    <svg
      className="h-6 w-6"
      aria-hidden="true"
      xmlns="http://www.w3.org/2000/svg"
      fill="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        fill-rule="evenodd"
        d="M2 12a10 10 0 1 1 20 0 10 10 0 0 1-20 0Zm11-4a1 1 0 1 0-2 0v5a1 1 0 1 0 2 0V8Zm-1 7a1 1 0 1 0 0 2 1 1 0 1 0 0-2Z"
        clip-rule="evenodd"
      />
    </svg>
  );
}

const ErrorBanner = ({ visible }) => {
  return (
    <Banner>
      <div
        className={`fixed start-0 top-0 z-50 flex w-full bg-red-200 p-2 text-red-900 dark:bg-red-900 dark:text-white ${visible ? "" : "hidden"}`}
      >
        <p className="mx-auto flex items-center gap-2 text-sm font-normal">
          <ErrorIcon /> 
          <span>Could not fetch API data. Please try again later.</span>
        </p>
      </div>
    </Banner>
  );
};

export default ErrorBanner;
