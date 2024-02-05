import "flowbite";

document.getElementById("goto-api").href = process.env.BACKEND_URL;

const themeToggleDarkIcon = document.getElementById("theme-toggle-dark-icon");
const themeToggleLightIcon = document.getElementById("theme-toggle-light-icon");

// Change the icons inside the button based on previous settings
if (
  localStorage.getItem("color-theme") === "dark" ||
  (!("color-theme" in localStorage) &&
    window.matchMedia("(prefers-color-scheme: dark)").matches)
) {
  themeToggleLightIcon.classList.remove("hidden");
} else {
  themeToggleDarkIcon.classList.remove("hidden");
}

const themeToggleBtn = document.getElementById("theme-toggle");

themeToggleBtn.addEventListener("click", function () {
  // toggle icons inside button
  themeToggleDarkIcon.classList.toggle("hidden");
  themeToggleLightIcon.classList.toggle("hidden");

  // if set via local storage previously
  if (localStorage.getItem("color-theme")) {
    if (localStorage.getItem("color-theme") === "light") {
      document.documentElement.classList.add("dark");
      localStorage.setItem("color-theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("color-theme", "light");
    }

    // if NOT set via local storage previously
  } else {
    if (document.documentElement.classList.contains("dark")) {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("color-theme", "light");
    } else {
      document.documentElement.classList.add("dark");
      localStorage.setItem("color-theme", "dark");
    }
  }
});

document.querySelectorAll("#default-tab li button").forEach((tab) => {
  const callback = (mutationsList) => {
    mutationsList.forEach((mutation) => {
      if (
        mutation.type === "attributes" &&
        mutation.attributeName === "aria-selected"
      ) {
        // Remove default classes
        mutation.target.classList.remove(
          ...[
            "text-blue-600",
            "hover:text-blue-600",
            "border-blue-600",
            "dark:text-blue-500",
            "dark:border-blue-500",
            "dark:hover:text-blue-500",
          ],
        );

        const classes = [
          "text-green-700",
          "border-green-700",
          "hover:text-green-600",
          "dark:border-green-300",
          "dark:text-green-300",
          "dark:hover:text-green-200",
        ];
        if (mutation.target.getAttribute("aria-selected") === "true") {
          mutation.target.classList.add(...classes);
        } else {
          mutation.target.classList.remove(...classes);
        }
      }
    });
  };

  new MutationObserver(callback).observe(tab, { attributes: true });
});

fetch(process.env.BACKEND_URL + "/consumption" + new Date().toISOString())
  .then((response) => {
    document.getElementById("total-consumption").innerText = response.value;
  })
  .catch((err) =>
    document.getElementById("api-error-banner").classList.remove("hidden"),
  );
