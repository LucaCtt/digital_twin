import { Button, Tooltip, useThemeMode } from "flowbite-react";
import { MdDarkMode, MdLightMode } from "react-icons/md";

const ThemeButton = () => {
  const { mode, setMode } = useThemeMode();

  return (
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
  );
};

export default ThemeButton;
