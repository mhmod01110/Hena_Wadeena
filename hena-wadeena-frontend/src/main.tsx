import { createRoot } from "react-dom/client";
import { ThemeProvider } from "next-themes";
import App from "./App.tsx";
import { I18nProvider } from "./i18n/I18nProvider";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <ThemeProvider attribute="class" defaultTheme="light" enableSystem>
    <I18nProvider>
      <App />
    </I18nProvider>
  </ThemeProvider>,
);
