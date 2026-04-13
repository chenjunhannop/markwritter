import { Menu, Monitor, Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useIsMobile } from "@/hooks/use-mobile";
import { useTheme } from "@/hooks/use-theme";
import { navItems } from "@/lib/nav-config";
import { useUiStore } from "@/stores/ui-store";

export function Header() {
  const theme = useTheme();
  const setTheme = useUiStore((s) => s.setTheme);
  const toggleSidebar = useUiStore((s) => s.toggleSidebar);
  const setDrawerOpen = useUiStore((s) => s.setDrawerOpen);
  const isMobile = useIsMobile();

  const currentPath = window.location.pathname;
  const currentNav = navItems.find((item) => item.path === currentPath);
  const pageTitle = currentNav?.label ?? "Markwritter";

  function cycleTheme() {
    const next =
      theme === "light" ? "dark" : theme === "dark" ? "system" : "light";
    setTheme(next);
  }

  const ThemeIcon = theme === "dark" ? Moon : theme === "light" ? Sun : Monitor;

  return (
    <header className="sticky top-0 z-10 flex h-14 items-center gap-4 border-b border-white/45 dark:border-white/15 bg-background/78 backdrop-blur-3xl backdrop-saturate-[180%] px-4 md:px-6">
      {isMobile && (
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={() => setDrawerOpen(true)}
        >
          <Menu className="h-5 w-5" />
        </Button>
      )}

      <h1 className="text-lg font-semibold">{pageTitle}</h1>

      <div className="ml-auto flex items-center gap-2">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="ghost" size="icon-sm" onClick={cycleTheme}>
              <ThemeIcon className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            {theme === "light"
              ? "浅色模式"
              : theme === "dark"
                ? "深色模式"
                : "跟随系统"}
          </TooltipContent>
        </Tooltip>

        {!isMobile && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon-sm" onClick={toggleSidebar}>
                <Menu className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>切换侧边栏</TooltipContent>
          </Tooltip>
        )}
      </div>
    </header>
  );
}
