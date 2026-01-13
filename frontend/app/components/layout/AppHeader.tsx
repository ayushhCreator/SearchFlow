"use client";

import { useTheme } from "../ThemeProvider";

interface AppHeaderProps {
  onToggleSidebar: () => void;
  onOpenSettings: () => void;
  lastModelUsed?: string;
}

export function AppHeader({ onToggleSidebar, onOpenSettings, lastModelUsed }: AppHeaderProps) {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="absolute top-0 left-0 right-0 p-4 z-40 flex justify-between items-center pointer-events-none">
      {/* Mobile Menu Button - Pointer events enabled */}
      <button
        onClick={onToggleSidebar}
        className="md:hidden pointer-events-auto p-2 bg-[var(--card)] border border-[var(--border)] rounded-lg text-[var(--muted)] shadow-sm"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      <div className="flex items-center gap-3 ml-auto pointer-events-auto">
        {/* Model Badge */}
        {lastModelUsed && (
          <div className="px-3 py-1.5 bg-[var(--card)]/80 backdrop-blur border border-[var(--border)] rounded-full text-xs text-[var(--muted)] font-mono shadow-sm">
            {lastModelUsed.split("/").pop()}
          </div>
        )}

        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          className="p-2.5 bg-[var(--card)] border border-[var(--border)] rounded-lg text-[var(--muted)] hover:text-[var(--foreground)] hover:bg-[var(--accent)] transition-all shadow-sm"
          title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
        >
          {theme === "dark" ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          )}
        </button>

        {/* Settings Button */}
        <button
          onClick={onOpenSettings}
          className="p-2.5 bg-[var(--card)] border border-[var(--border)] rounded-lg text-[var(--muted)] hover:text-[var(--foreground)] hover:bg-[var(--accent)] transition-all shadow-sm"
          title="Settings"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>
      </div>
    </header>
  );
}
