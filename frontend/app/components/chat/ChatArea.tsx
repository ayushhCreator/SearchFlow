"use client";

import React from "react";
import { MarkdownContent } from "../MarkdownContent";
import { SourceCard } from "../SourceCard";
import { ThinkingAnimation } from "../ThinkingAnimation";

interface ChatAreaProps {
  currentThread: any;
  state: any;
  statusMessage: string;
  onDownload: (content: string, id: string) => void;
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
  suggestions: string[];
  isLoadingSuggestions: boolean;
  onSearch: (query: string) => void;
}

export function ChatArea({
  currentThread,
  state,
  statusMessage,
  onDownload,
  messagesEndRef,
  suggestions,
  isLoadingSuggestions,
  onSearch,
}: ChatAreaProps) {

  if (!currentThread || currentThread.messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-4 text-center animate-in fade-in zoom-in-95 duration-500">
        <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[var(--primary)] to-purple-500 mb-8 p-1">
          SearchFlow AI
        </h1>

        <div className="max-w-md w-full">
          <h2 className="text-[var(--muted)] mb-4 text-sm font-medium uppercase tracking-wider">
            {isLoadingSuggestions ? "Loading suggestions..." : "Suggested Queries"}
          </h2>

          <div className="grid gap-2">
            {suggestions.map((q, i) => (
              <button
                key={i}
                onClick={() => onSearch(q)}
                className="w-full p-4 text-left text-sm text-[var(--foreground)] bg-[var(--card)] border border-[var(--border)] rounded-xl hover:bg-[var(--accent)] hover:border-[var(--primary)]/30 hover:shadow-lg transition-all duration-300 group"
              >
                <span className="group-hover:text-[var(--primary)] transition-colors">{q}</span>
              </button>
            ))}
            {!isLoadingSuggestions && suggestions.length === 0 && (
               <div className="text-[var(--muted)] text-sm italic">No suggestions available. Try searching!</div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-8 mb-32 space-y-12 px-4">
      {currentThread.messages.map((message: any) => (
        <div key={message.id}>
          {message.role === "user" ? (
            <div className="flex justify-end mb-8">
              <div className="bg-[var(--accent)] text-[var(--foreground)] px-5 py-3 rounded-2xl rounded-br-sm max-w-[85%] text-lg shadow-sm">
                {message.content}
              </div>
            </div>
          ) : (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 group">
              {/* Answer */}
              <div className="prose dark:prose-invert max-w-none text-[var(--foreground)] leading-relaxed">
                <MarkdownContent content={message.content} sources={message.context} />
              </div>

              {/* Actions */}
              <div className="flex items-center gap-4 mt-4 pt-4 border-t border-[var(--border)] opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => onDownload(message.content, message.id)}
                  className="text-xs text-[var(--muted)] hover:text-[var(--foreground)] flex items-center gap-1.5 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download MD
                </button>
                {message.confidence && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-[var(--primary)]/10 text-[var(--primary)] font-medium">
                    {Math.round(message.confidence * 100)}% Confidence
                  </span>
                )}
                {message.model_used && (
                  <span className="text-xs text-[var(--muted)] font-mono ml-auto">
                    {message.model_used}
                  </span>
                )}
              </div>

              {/* Sources Grid */}
              {(message.context?.length || 0) > 0 && (
                <div className="mt-8">
                  <div className="flex items-center gap-2 mb-3">
                    <h4 className="text-xs font-semibold text-[var(--muted)] uppercase tracking-wider">
                      Sources
                    </h4>
                    <div className="h-px flex-1 bg-[var(--border)]"></div>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    {message.context?.map((source: any, idx: number) => (
                      <SourceCard key={idx} source={source} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      ))}

      {/* Searching State */}
      {state.status === "searching" && (
        <div className="flex flex-col items-start gap-4 py-8 animate-in fade-in slide-in-from-bottom-4">
          <ThinkingAnimation message={statusMessage || "Thinking..."} />
        </div>
      )}

      {/* Streaming State */}
      {state.status === "streaming" && (
        <div className="animate-in fade-in">
          <div className="prose dark:prose-invert max-w-none text-[var(--foreground)]">
            <MarkdownContent content={state.currentAnswer + "▌"} />
          </div>
          <div className="mt-4">
            <ThinkingAnimation message={statusMessage || "Generating answer..."} />
          </div>
        </div>
      )}

      <div ref={messagesEndRef} className="h-4" />
    </div>
  );
}
