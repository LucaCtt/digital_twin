import { MdLightbulbCircle } from "react-icons/md";
import ThemeButton from "./ThemeButton";
import ApiDocsButton from "./ApiDocsButton";

const TitleBar = () => {
  return (
    <header className="flex w-full flex-col items-center justify-between gap-4 rounded-lg bg-green-100 p-8 dark:border-gray-700 dark:bg-green-900 md:flex-row">
      <div className="flex flex-row items-center justify-between gap-4 leading-normal">
        <MdLightbulbCircle className="h-32 w-32 rounded-full text-green-700 dark:border-green-300 dark:text-green-300 md:h-24 md:h-24" />
        <h1 className="mb-0">Digital Twin Showcase</h1>
      </div>

      <div className="flex flex-row items-center justify-center gap-2">
        <ThemeButton />
        <ApiDocsButton />
      </div>
    </header>
  );
};

export default TitleBar;
