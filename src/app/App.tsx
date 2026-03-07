import { RouterProvider } from "react-router-dom";
import { router } from "./routes";
import { AppDataProvider } from "./api/Client";

export default function App() {
  return (
    <AppDataProvider>
      <RouterProvider router={router} />
    </AppDataProvider>
  );
}
