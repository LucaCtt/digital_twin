import { Button, Tooltip, useThemeMode } from "flowbite-react";
import {
  MdMenuBook,
  MdDarkMode,
  MdLightMode,
  MdLightbulbCircle,
} from "react-icons/md";

const Title = () => {
  const { mode, setMode } = useThemeMode();
  return (
    <header className="flex w-full flex-col items-center justify-between gap-4 rounded-lg bg-green-100 p-8 dark:border-gray-700 dark:bg-green-900 md:flex-row">
      <div className="flex flex-row items-center justify-between gap-4 leading-normal">
        <MdLightbulbCircle className="h-32 md:h-24 w-32 md:h-24 rounded-full text-green-700 dark:border-green-300 dark:text-green-300" />
        <h1 className="mb-0">Digital Twin Showcase</h1>
      </div>

      <div className="flex flex-row items-center justify-center gap-2">
        <Tooltip content="Toggle dark mode">
          <Button
            className="b-0 rounded-full bg-transparent text-gray-900 focus:outline-none focus:ring-4 focus:ring-green-300 enabled:hover:bg-green-200 dark:bg-transparent dark:text-white dark:focus:ring-green-700 dark:enabled:hover:bg-green-800"
            onClick={() => setMode(mode === "dark" ? "light" : "dark")}
          >
            {mode === "dark" ? (
              <MdDarkMode className="h-6 w-6" />
            ) : (
              <MdLightMode className="h-6 w-6" />
            )}
          </Button>
        </Tooltip>

        <Tooltip content="Go to API docs">
          <a href={process.env.BACKEND_URL}>
            <Button className="b-0 items-center rounded-full bg-transparent text-gray-900 focus:outline-none focus:ring-4 focus:ring-green-300 enabled:hover:bg-green-200 dark:bg-transparent dark:text-white dark:focus:ring-green-700 dark:enabled:hover:bg-green-800">
              <MdMenuBook className="h-6 w-6" />
            </Button>
          </a>
        </Tooltip>
      </div>
    </header>
  );
};
export default Title;
