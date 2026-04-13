import type { ReactNode } from "react";
import { BackgroundMesh } from "@/components/shared/background-mesh";
import { TooltipProvider } from "@/components/ui/tooltip";
import { useIsMobile } from "@/hooks/use-mobile";
import { useTheme } from "@/hooks/use-theme";
import { Header } from "./header";
import { MobileDrawer } from "./mobile-drawer";
import { Sidebar } from "./sidebar";

export function AppLayout({ children }: { children: ReactNode }) {
  useTheme();
  const isMobile = useIsMobile();

  return (
    <TooltipProvider delayDuration={0}>
      <div className="relative h-screen w-screen overflow-hidden">
        <BackgroundMesh />

        <div className="relative flex h-full">
          {!isMobile && <Sidebar />}

          <div className="flex flex-1 flex-col min-w-0">
            <Header />
            <main className="flex-1 overflow-auto relative">{children}</main>
          </div>

          {isMobile && <MobileDrawer />}
        </div>
      </div>
    </TooltipProvider>
  );
}
