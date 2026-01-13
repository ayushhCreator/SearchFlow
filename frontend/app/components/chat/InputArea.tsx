"use client";

import React, { useEffect, useRef } from "react";

interface InputAreaProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
  onStop?: () => void; // Optional stop generation
}

export function InputArea({ onSearch, isLoading, onStop }: InputAreaProps) {
  const [input, setInput] = React.useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;
    onSearch(input);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  return (
    <div className="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-[var(--background)] via-[var(--background)] to-transparent pt-12 pb-6 z-20">
      <div className="max-w-3xl mx-auto relative group">
        <form onSubmit={handleSubmit} className="relative bg-[var(--card)] rounded-2xl shadow-2xl border border-[var(--border)] transition-all focus-within:ring-2 focus-within:ring-[var(--primary)] focus-within:border-transparent">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything..."
            className="w-full bg-transparent text-[var(--foreground)] placeholder-[var(--muted)] px-4 py-4 pr-14 text-base resize-none focus:outline-none max-h-[200px] overflow-y-auto rounded-2xl scrollbar-hide"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() && !isLoading}
            className={`absolute right-2 bottom-2 p-2 rounded-xl transition-all ${
              input.trim()
                ? "bg-[var(--primary)] text-[var(--primary-foreground)] hover:opacity-90"
                : "bg-[var(--accent)] text-[var(--muted)] cursor-not-allowed"
            }`}
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-[var(--primary-foreground)]/30 border-t-[var(--primary-foreground)] rounded-full animate-spin" />
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            )}
          </button>
        </form>
        <div className="text-center mt-3">
          <p className="text-xs text-[var(--muted)]">
            SearchFlow can make mistakes. Verify important info.
          </p>
        </div>
      </div>
    </div>
  );
}
