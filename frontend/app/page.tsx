"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// API Configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8007";

// Types
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  confidence?: number;
  cached?: boolean;
  timestamp: number;
}

interface ChatThread {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
}

interface SearchState {
  status: "idle" | "searching" | "streaming" | "done" | "error";
  currentAnswer: string;
  error?: string;
}

// Local storage helpers
const STORAGE_KEY = "searchflow_threads";

function loadThreads(): ChatThread[] {
  if (typeof window === "undefined") return [];
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

function saveThreads(threads: ChatThread[]) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(threads));
}

// Generate unique ID
function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2);
}

// Code block component
function CodeBlock({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  const language = className?.replace("language-", "") || "";
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const code = String(children).replace(/\n$/, "");
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative my-4 rounded-lg overflow-hidden group">
      {language && (
        <div className="absolute top-0 left-0 px-2 py-1 text-xs text-zinc-500 bg-zinc-800/50 rounded-br">
          {language}
        </div>
      )}
      <button
        onClick={handleCopy}
        className="absolute top-2 right-2 px-2 py-1 text-xs text-zinc-500 bg-zinc-800 rounded opacity-0 group-hover:opacity-100 transition-opacity hover:text-zinc-300"
      >
        {copied ? "Copied!" : "Copy"}
      </button>
      <pre className="bg-zinc-900 border border-zinc-800 p-4 pt-8 overflow-x-auto">
        <code className={`text-sm font-mono text-zinc-300 ${className || ""}`}>
          {children}
        </code>
      </pre>
    </div>
  );
}

function InlineCode({ children }: { children: React.ReactNode }) {
  return (
    <code className="px-1.5 py-0.5 bg-zinc-800 text-blue-300 rounded text-sm font-mono">
      {children}
    </code>
  );
}

// Markdown renderer component
function MarkdownContent({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ className, children }) {
          const isInline = !className;
          if (isInline) {
            return <InlineCode>{children}</InlineCode>;
          }
          return <CodeBlock className={className}>{children}</CodeBlock>;
        },
        h1: ({ children }) => (
          <h1 className="text-xl font-semibold text-zinc-200 mt-6 mb-3">
            {children}
          </h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-lg font-semibold text-zinc-200 mt-5 mb-2">
            {children}
          </h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-base font-semibold text-zinc-300 mt-4 mb-2">
            {children}
          </h3>
        ),
        p: ({ children }) => (
          <p className="text-zinc-300 leading-relaxed mb-4 text-base">
            {children}
          </p>
        ),
        ul: ({ children }) => (
          <ul className="list-disc list-inside text-zinc-300 mb-4 space-y-1">
            {children}
          </ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal list-inside text-zinc-300 mb-4 space-y-1">
            {children}
          </ol>
        ),
        a: ({ href, children }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:text-blue-300 underline"
          >
            {children}
          </a>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-2 border-zinc-600 pl-4 italic text-zinc-400 my-4">
            {children}
          </blockquote>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

export default function Home() {
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [currentThreadId, setCurrentThreadId] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [state, setState] = useState<SearchState>({
    status: "idle",
    currentAnswer: "",
  });
  const [statusMessage, setStatusMessage] = useState("");
  const [showSidebar, setShowSidebar] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load threads on mount
  useEffect(() => {
    setThreads(loadThreads());
  }, []);

  // Save threads when they change
  useEffect(() => {
    if (threads.length > 0) {
      saveThreads(threads);
    }
  }, [threads]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [state.currentAnswer, currentThread?.messages]);

  // Get current thread
  const currentThread = threads.find((t) => t.id === currentThreadId);

  // Create new thread
  const createNewThread = () => {
    const newThread: ChatThread = {
      id: generateId(),
      title: "New Chat",
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };
    setThreads((prev) => [newThread, ...prev]);
    setCurrentThreadId(newThread.id);
    setQuery("");
    setState({ status: "idle", currentAnswer: "" });
  };

  // Delete thread
  const deleteThread = (threadId: string) => {
    setThreads((prev) => prev.filter((t) => t.id !== threadId));
    if (currentThreadId === threadId) {
      setCurrentThreadId(null);
    }
  };

  // Search handler
  const handleSearch = async () => {
    if (!query.trim()) return;

    const userQuery = query.trim();
    setQuery("");

    // Create thread if none exists
    let threadId = currentThreadId;
    if (!threadId) {
      const newThread: ChatThread = {
        id: generateId(),
        title: userQuery.slice(0, 50),
        messages: [],
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };
      setThreads((prev) => [newThread, ...prev]);
      threadId = newThread.id;
      setCurrentThreadId(threadId);
    }

    // Add user message
    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content: userQuery,
      timestamp: Date.now(),
    };

    setThreads((prev) =>
      prev.map((t) =>
        t.id === threadId
          ? {
              ...t,
              messages: [...t.messages, userMessage],
              title: t.messages.length === 0 ? userQuery.slice(0, 50) : t.title,
              updatedAt: Date.now(),
            }
          : t
      )
    );

    // Start searching
    setState({ status: "searching", currentAnswer: "" });
    setStatusMessage("Connecting...");

    try {
      const response = await fetch(`${API_URL}/api/v1/search/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userQuery }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) throw new Error("No response body");

      let buffer = "";
      let fullAnswer = "";
      let sources: string[] = [];
      let confidence = 0;
      let cached = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data:")) {
            const dataStr = line.slice(5).trim();
            if (!dataStr) continue;

            try {
              const data = JSON.parse(dataStr);

              if (data.message) {
                setStatusMessage(data.message);
              } else if (data.content !== undefined) {
                fullAnswer += data.content;
                setState((prev) => ({
                  ...prev,
                  status: "streaming",
                  currentAnswer: fullAnswer,
                }));
                setStatusMessage("");
              } else if (data.sources !== undefined) {
                sources = data.sources || [];
                confidence = data.confidence || 0;
                cached = data.cached || false;
              }
            } catch {
              // Ignore parse errors
            }
          }
        }
      }

      // Add assistant message
      const assistantMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: fullAnswer,
        sources,
        confidence,
        cached,
        timestamp: Date.now(),
      };

      setThreads((prev) =>
        prev.map((t) =>
          t.id === threadId
            ? {
                ...t,
                messages: [...t.messages, assistantMessage],
                updatedAt: Date.now(),
              }
            : t
        )
      );

      setState({ status: "done", currentAnswer: "" });
    } catch (err) {
      setState({
        status: "error",
        currentAnswer: "",
        error: err instanceof Error ? err.message : "Connection failed",
      });
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const isLoading =
    state.status === "searching" || state.status === "streaming";

  return (
    <div className="flex h-screen bg-zinc-950">
      {/* Sidebar */}
      <aside
        className={`${
          showSidebar ? "translate-x-0" : "-translate-x-full"
        } md:translate-x-0 fixed md:relative z-40 w-64 h-full bg-zinc-900 border-r border-zinc-800 transition-transform duration-300 flex flex-col`}
      >
        {/* New Chat Button */}
        <div className="p-4 border-b border-zinc-800">
          <button
            onClick={createNewThread}
            className="w-full py-2 px-4 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Thread List */}
        <div className="flex-1 overflow-y-auto p-2">
          {threads.map((thread) => (
            <div
              key={thread.id}
              className={`group flex items-center gap-2 p-3 rounded-lg cursor-pointer mb-1 ${
                currentThreadId === thread.id
                  ? "bg-zinc-800"
                  : "hover:bg-zinc-800/50"
              }`}
              onClick={() => {
                setCurrentThreadId(thread.id);
                setState({ status: "idle", currentAnswer: "" });
                setShowSidebar(false);
              }}
            >
              <svg className="w-4 h-4 text-zinc-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <span className="text-sm text-zinc-300 truncate flex-1">
                {thread.title}
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteThread(thread.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 text-zinc-500 hover:text-red-400 transition-all"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-zinc-800 text-xs text-zinc-600">
          SearchFlow v1.0
        </div>
      </aside>

      {/* Mobile sidebar toggle */}
      <button
        onClick={() => setShowSidebar(!showSidebar)}
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-zinc-800 rounded-lg"
      >
        <svg className="w-5 h-5 text-zinc-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 py-8">
          <div className="max-w-3xl mx-auto">
            {!currentThread || currentThread.messages.length === 0 ? (
              // Welcome screen
              <div className="flex flex-col items-center justify-center h-full text-center">
                <h1 className="text-3xl font-light tracking-[0.3em] text-zinc-200 mb-2">
                  SEARCHFLOW
                </h1>
                <p className="text-sm text-zinc-500 font-light mb-8">
                  structured knowledge from the web
                </p>
                <p className="text-zinc-600 text-sm">
                  Start a conversation by typing a question below
                </p>
              </div>
            ) : (
              // Messages
              <div className="space-y-6">
                {currentThread.messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[85%] ${
                        message.role === "user"
                          ? "bg-blue-600/20 border border-blue-500/30 rounded-2xl rounded-br-sm px-4 py-3"
                          : ""
                      }`}
                    >
                      {message.role === "user" ? (
                        <p className="text-zinc-200">{message.content}</p>
                      ) : (
                        <div>
                          <MarkdownContent content={message.content} />
                          {message.sources && message.sources.length > 0 && (
                            <div className="mt-4 pt-4 border-t border-zinc-800">
                              <div className="flex items-center gap-4 text-xs text-zinc-600 mb-2">
                                {message.confidence && message.confidence > 0 && (
                                  <span>
                                    confidence: {Math.round(message.confidence * 100)}%
                                  </span>
                                )}
                                {message.cached && (
                                  <span className="text-blue-400/60">cached</span>
                                )}
                              </div>
                              <div className="flex flex-wrap gap-2">
                                {message.sources.map((url, i) => (
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
                    </div>
                  </div>
                ))}

                {/* Streaming answer */}
                {state.status === "streaming" && state.currentAnswer && (
                  <div className="flex justify-start">
                    <div className="max-w-[85%]">
                      <div className="cursor">
                        <MarkdownContent content={state.currentAnswer} />
                      </div>
                    </div>
                  </div>
                )}

                {/* Status message */}
                {statusMessage && (
                  <div className="text-sm text-zinc-500 pulse">{statusMessage}</div>
                )}

                {/* Error */}
                {state.status === "error" && (
                  <div className="text-red-400/80 text-sm">{state.error}</div>
                )}

                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-zinc-800 p-4">
          <div className="max-w-3xl mx-auto">
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
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                )}
              </button>
            </div>
            <p className="text-center text-xs text-zinc-700 mt-3">
              powered by DSPy + SearXNG
            </p>
          </div>
        </div>
      </main>

      {/* Sidebar overlay for mobile */}
      {showSidebar && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-30"
          onClick={() => setShowSidebar(false)}
        />
      )}
    </div>
  );
}
