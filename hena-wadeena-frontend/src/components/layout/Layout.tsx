import { ReactNode } from "react";
import { Header } from "./Header";
import { Footer } from "./Footer";
import { useI18n } from "@/i18n/I18nProvider";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { direction } = useI18n();

  return (
    <div className="min-h-screen flex flex-col" dir={direction}>
      <Header />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
}
