"use client";

import { useEffect, useRef, useState } from "react";

// API Configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8007";

interface Source {
  title?: string;
  url: string;
  snippet?: string;
}

interface SearchState {
  status: "idle" | "searching" | "streaming" | "done" | "error";
  answer: string;
  sources: string[];
  confidence: number;
  cached: boolean;
  error?: string;
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [state, setState] = useState<SearchState>({
    status: "idle",
    answer: "",
    sources: [],
    confidence: 0,
    cached: false,
  });
  const [statusMessage, setStatusMessage] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const answerRef = useRef<HTMLDivElement>(null);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Auto-scroll answer area
  useEffect(() => {
    if (answerRef.current) {
      answerRef.current.scrollTop = answerRef.current.scrollHeight;
    }
  }, [state.answer]);

  const handleSearch = async () => {
    if (!query.trim()) return;

    // Reset state
    setState({
      status: "searching",
      answer: "",
      sources: [],
      confidence: 0,
      cached: false,
    });
    setStatusMessage("Connecting...");

    try {
      const response = await fetch(`${API_URL}/api/v1/search/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query.trim() }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error("No response body");

      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("event:")) {
            const eventType = line.slice(6).trim();
            continue;
          }

          if (line.startsWith("data:")) {
            const dataStr = line.slice(5).trim();
            if (!dataStr) continue;

            try {
              const data = JSON.parse(dataStr);

              // Handle different event types based on data content
              if (data.message) {
                setStatusMessage(data.message);
                setState((prev) => ({ ...prev, status: "searching" }));
              } else if (data.content !== undefined) {
                setState((prev) => ({
                  ...prev,
                  status: "streaming",
                  answer: prev.answer + data.content,
                }));
                setStatusMessage("");
              } else if (data.sources !== undefined) {
                setState((prev) => ({
                  ...prev,
                  status: "done",
                  sources: data.sources || [],
                  confidence: data.confidence || 0,
                  cached: data.cached || false,
                }));
              } else if (data.error) {
                setState((prev) => ({
                  ...prev,
                  status: "error",
                  error: data.error,
                }));
              }
            } catch {
              // Ignore parse errors for malformed lines
            }
          }
        }
      }
    } catch (err) {
      setState((prev) => ({
        ...prev,
        status: "error",
        error: err instanceof Error ? err.message : "Connection failed",
      }));
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const isLoading = state.status === "searching" || state.status === "streaming";

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-6 py-12">
      {/* Header */}
      <div className="text-center mb-12 fade-in">
        <h1 className="text-3xl font-light tracking-[0.3em] text-zinc-200 mb-2">
          SEARCHFLOW
        </h1>
        <p className="text-sm text-zinc-500 font-light">
          structured knowledge from the web
        </p>
      </div>

      {/* Search Input */}
      <div className="w-full max-w-2xl mb-8 fade-in">
        <div
          className={`relative border rounded-xl transition-all duration-300 ${
            isLoading
              ? "border-blue-500/50 glow"
              : "border-zinc-800 hover:border-zinc-700 focus-within:border-zinc-600"
          }`}
        >
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="What would you like to know?"
            disabled={isLoading}
            className="w-full bg-transparent px-5 py-4 text-lg text-zinc-100 placeholder:text-zinc-600 focus:outline-none disabled:opacity-50"
          />
          <button
            onClick={handleSearch}
            disabled={isLoading || !query.trim()}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-zinc-500 hover:text-zinc-300 disabled:opacity-30 transition-colors"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-zinc-500 border-t-transparent rounded-full animate-spin" />
            ) : (
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M13 7l5 5m0 0l-5 5m5-5H6"
                />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Status Message */}
      {statusMessage && (
        <div className="text-sm text-zinc-500 mb-4 fade-in">
          <span className="pulse">{statusMessage}</span>
        </div>
      )}

      {/* Answer Area */}
      {(state.answer || state.status === "error") && (
        <div className="w-full max-w-2xl fade-in">
          {/* Divider */}
          <div className="h-px bg-zinc-800 mb-6" />

          {state.status === "error" ? (
            <div className="text-red-400/80 text-sm">
              {state.error || "Something went wrong"}
            </div>
          ) : (
            <>
              {/* Answer Text */}
              <div
                ref={answerRef}
                className={`text-zinc-300 leading-relaxed text-lg font-light max-h-96 overflow-y-auto ${
                  state.status === "streaming" ? "cursor" : ""
                }`}
              >
                {state.answer}
              </div>

              {/* Metadata */}
              {state.status === "done" && (
                <div className="mt-8 fade-in">
                  {/* Confidence & Cache */}
                  <div className="flex items-center gap-4 text-xs text-zinc-600 mb-4">
                    {state.confidence > 0 && (
                      <span>
                        confidence: {Math.round(state.confidence * 100)}%
                      </span>
                    )}
                    {state.cached && (
                      <span className="text-blue-400/60">cached</span>
                    )}
                  </div>

                  {/* Sources */}
                  {state.sources.length > 0 && (
                    <div>
                      <div className="text-xs text-zinc-600 mb-3">
                        sources ({state.sources.length})
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {state.sources.map((url, i) => (
                          <a
                            key={i}
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="source-dot"
                            title={url}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="fixed bottom-6 text-xs text-zinc-700">
        powered by DSPy + SearXNG
      </div>
    </main>
  );
}
