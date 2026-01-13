"use client";

import { useTheme } from "./ThemeProvider";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentModel?: string;
}

export function SettingsModal({
  isOpen,
  onClose,
  currentModel,
}: SettingsModalProps) {
  const { theme, setTheme } = useTheme();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[var(--card)] border border-[var(--border)] rounded-2xl w-full max-w-md shadow-2xl animate-in zoom-in-95 duration-200">

        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-[var(--border)]">
          <h2 className="text-xl font-bold text-[var(--foreground)]">
            Settings
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-[var(--muted)] hover:bg-[var(--accent)] hover:text-[var(--foreground)] transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Current Model */}
          {currentModel && (
            <div>
              <label className="block text-sm font-medium text-[var(--foreground)] mb-2">
                AI Model (Server Configured)
              </label>
              <div className="w-full px-4 py-3 rounded-xl border border-[var(--border)] bg-[var(--sidebar)] text-[var(--muted)] font-mono text-sm">
                {currentModel}
              </div>
            </div>
          )}

          {/* Theme Selector */}
          <div>
            <label className="block text-sm font-medium text-[var(--foreground)] mb-2">
              Appearance
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setTheme("dark")}
                className={`
                  flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-medium transition-all border
                  ${theme === "dark"
                    ? "bg-[var(--primary)] text-[var(--primary-foreground)] border-transparent shadow-lg shadow-blue-500/20"
                    : "bg-[var(--sidebar)] text-[var(--muted)] border-[var(--border)] hover:bg-[var(--accent)] hover:text-[var(--foreground)]"
                  }
                `}
              >
                <span className="text-lg">🌙</span>
                Dark
              </button>
              <button
                onClick={() => setTheme("light")}
                className={`
                  flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-medium transition-all border
                  ${theme === "light"
                    ? "bg-[var(--primary)] text-[var(--primary-foreground)] border-transparent shadow-lg shadow-blue-500/20"
                    : "bg-[var(--sidebar)] text-[var(--muted)] border-[var(--border)] hover:bg-[var(--accent)] hover:text-[var(--foreground)]"
                  }
                `}
              >
                <span className="text-lg">☀️</span>
                Light
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 pt-0">
          <button
            onClick={onClose}
            className="w-full py-3 bg-[var(--primary)] text-[var(--primary-foreground)] hover:opacity-90 rounded-xl font-medium transition-all shadow-lg"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}

// Export Theme type for compatibility if needed elsewhere
export type { Theme } from "./ThemeProvider";
