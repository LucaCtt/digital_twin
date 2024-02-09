import { Button, Tooltip } from "flowbite-react";
import { MdMenuBook } from "react-icons/md";

const ApiDocsButton = () => (
  <Tooltip content="Go to API docs">
    <a href={import.meta.env.DT_BACKEND_URL}>
      <Button className="b-0 items-center rounded-full bg-transparent text-gray-900 focus:outline-none focus:ring-4 focus:ring-green-300 enabled:hover:bg-green-200 dark:bg-transparent dark:text-white dark:focus:ring-green-700 dark:enabled:hover:bg-green-800">
        <MdMenuBook className="h-6 w-6" />
      </Button>
    </a>
  </Tooltip>
);

export default ApiDocsButton;
