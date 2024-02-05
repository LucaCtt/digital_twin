import { DarkThemeToggle, Tooltip } from "flowbite-react";

const Logo = () => (
  <svg
    className="h-14 w-14 rounded-full border-2 border-green-700 p-2 text-green-700 dark:border-green-300 dark:text-green-300"
    aria-hidden="true"
    xmlns="http://www.w3.org/2000/svg"
    fill="currentColor"
    viewBox="0 0 15 20"
  >
    <path d="M9.092 18h-4a1 1 0 0 0 0 2h4a1 1 0 0 0 0-2Zm-2-18a7.009 7.009 0 0 0-7 7 7.8 7.8 0 0 0 2.219 5.123c.956 1.195 1.781 2.228 1.781 3.877a1 1 0 0 0 1 1h4a1 1 0 0 0 1-1c0-1.7.822-2.7 1.774-3.868A7.63 7.63 0 0 0 14.092 7a7.009 7.009 0 0 0-7-7Zm0 5a2 2 0 0 0-2 2 1 1 0 0 1-2 0 4 4 0 0 1 4-4 1 1 0 0 1 0 2Z" />
  </svg>
);

const ApiIcon = () => (
  <svg
    className="h-6 w-6"
    fill="currentColor"
    aria-hidden="true"
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
  >
    <path
      fill-rule="evenodd"
      d="M11 4.7C8.7 4.1 6.8 4 4 4a2 2 0 0 0-2 2v11c0 1.1 1 2 2 2 2.8 0 4.5.2 7 .8v-15Zm2 15.1c2.5-.6 4.2-.8 7-.8a2 2 0 0 0 2-2V6c0-1-.9-2-2-2-2.8 0-4.7.1-7 .7v15.1Z"
      clip-rule="evenodd"
    />
  </svg>
);

const Title = () => (
  <header className="flex w-full flex-row items-center justify-between rounded-lg bg-green-100 p-4 dark:border-gray-700 dark:bg-green-900">
    <div className="flex flex-row items-center justify-between gap-8 p-4 leading-normal">
      <Logo />
      <h1 className="mb-0">Digital Twin Showcase</h1>
    </div>

    <div className="flex flex-row items-center justify-center gap-2">
      <Tooltip content="Toggle dark mode">
        <DarkThemeToggle className="rounded-full p-2.5 text-sm text-gray-900 hover:bg-green-200 focus:outline-none focus:ring-4 focus:ring-green-300 dark:text-white dark:hover:bg-green-800 dark:focus:ring-green-700" />
      </Tooltip>

      <Tooltip content="Go to API docs">
        <a
          href={process.env.BACKEND_URL}
          type="button"
          className="rounded-full p-2.5 text-sm text-gray-900 hover:bg-green-200 focus:outline-none focus:ring-4 focus:ring-green-300 dark:text-white dark:hover:bg-green-800 dark:focus:ring-green-700"
        >
          <ApiIcon />
        </a>
      </Tooltip>
    </div>
  </header>
);

export default Title;
