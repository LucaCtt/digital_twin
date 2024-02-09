import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig(({mode}) => {
  const env = loadEnv(mode, process.cwd(), "DT_");
  const port = env.DT_FRONTEND_URL.split(":")[2];

  return {
    server: {
      port: Number(port),
    },
    envDir: "../",
    envPrefix: "DT_",
    root: "frontend",
    plugins: [react()],
  };
});
