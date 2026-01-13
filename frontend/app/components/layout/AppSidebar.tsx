"use client";


export interface ChatThread {
  id: string;
  title: string;
  messages: any[]; // simplified for sidebar
  createdAt: number;
  updatedAt: number;
}

interface AppSidebarProps {
  threads: ChatThread[];
  currentThreadId: string | null;
  onSelectThread: (id: string) => void;
  onNewChat: () => void;
  isOpen: boolean;
  onClose: () => void;
}

function formatDate(timestamp: number) {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days === 0) return "Today";
  if (days === 1) return "Yesterday";
  if (days < 7) return "Previous 7 Days";
  return "Older";
}

export function AppSidebar({
  threads,
  currentThreadId,
  onSelectThread,
  onNewChat,
  isOpen,
  onClose,
}: AppSidebarProps) {
  // Group threads
  const groupedThreads: { [key: string]: ChatThread[] } = {};
  threads.forEach((thread) => {
    const label = formatDate(thread.updatedAt);
    if (!groupedThreads[label]) groupedThreads[label] = [];
    groupedThreads[label].push(thread);
  });

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden backdrop-blur-sm"
          onClick={onClose}
        />
      )}

      {/* Sidebar Content */}
      <aside
        className={`
          fixed top-0 left-0 h-full bg-[var(--sidebar)] border-r border-[var(--border)] z-50
          transition-transform duration-300 w-72 flex flex-col justify-between
          ${isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b border-[var(--border)]">
            <button
              onClick={onNewChat}
              className="w-full py-3 px-4 bg-[var(--primary)] text-[var(--primary-foreground)] rounded-xl font-medium shadow-lg hover:opacity-90 transition-all flex items-center justify-center gap-2 group"
            >
              <svg className="w-5 h-5 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Chat
            </button>
          </div>

          {/* Thread List */}
          <div className="flex-1 overflow-y-auto p-3 space-y-6">
            {Object.entries(groupedThreads).map(([label, groupThreads]) => (
              <div key={label}>
                <h3 className="text-xs font-semibold text-[var(--muted)] uppercase tracking-wider mb-3 px-3">
                  {label}
                </h3>
                <div className="space-y-1">
                  {groupThreads.map((thread) => (
                    <button
                      key={thread.id}
                      onClick={() => {
                        onSelectThread(thread.id);
                        if (window.innerWidth < 768) onClose();
                      }}
                      className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-all truncate flex items-center gap-3 ${
                        currentThreadId === thread.id
                          ? "bg-[var(--accent)] text-[var(--foreground)] font-medium"
                          : "text-[var(--muted)] hover:bg-[var(--accent)]/50 hover:text-[var(--foreground)]"
                      }`}
                    >
                      <svg className="w-4 h-4 shrink-0 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                      </svg>
                      <span className="truncate">{thread.title}</span>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-[var(--border)]">
            <div className="text-xs text-[var(--muted)] text-center font-mono">
              SEARCHFLOW AI v1.3
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
