"use client";

import { useEffect, useRef, useState } from "react";
import {
  AppHeader,
  AppSidebar,
  ChatArea,
  InputArea,
  SettingsModal,
  type Source
} from "./components";

function generateId() {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

// API Configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8007";
const MAX_RETRIES = 3;

// --- Types ---
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[]; // Legacy URL list
  context?: Source[]; // Rich context objects
  confidence?: number;
  cached?: boolean;
  model_used?: string; // Which LLM model was used
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

const STORAGE_KEY = "searchflow_threads";
const HISTORY_KEY = "searchflow_history";

// --- Helpers ---
function loadThreads(): ChatThread[] {
  if (typeof window === "undefined") return [];
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch (e) {
    console.error("Failed to load threads:", e);
    return [];
  }
}

function loadHistory(): string[] {
  if (typeof window === "undefined") return [];
  try {
    const data = localStorage.getItem(HISTORY_KEY);
    return data ? JSON.parse(data) : [];
  } catch (e) {
    return [];
  }
}

function saveHistory(query: string) {
  try {
    const history = loadHistory();
    // Add new query to beginning, remove duplicates, limit to 20
    const newHistory = [query, ...history.filter((q) => q !== query)].slice(0, 20);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(newHistory));
  } catch (e) {
    console.error("Failed to save history:", e);
  }
}

// --- Main Component ---
export default function Home() {
  // State
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [currentThreadId, setCurrentThreadId] = useState<string | null>(null);
  const [state, setState] = useState<SearchState>({
    status: "idle",
    currentAnswer: "",
  });
  const [statusMessage, setStatusMessage] = useState("");
  const [showSidebar, setShowSidebar] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [lastModelUsed, setLastModelUsed] = useState<string>("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load threads on mount
  useEffect(() => {
    setThreads(loadThreads());
  }, []);

  // Initialize new thread if none selected
  useEffect(() => {
    if (threads.length > 0 && !currentThreadId) {
       // Optional: Auto-select latest thread or start new one
       // For now, let's start fresh if no selection
    }
  }, [threads, currentThreadId]);

  // Load suggestions
  useEffect(() => {
    async function fetchSuggestions() {
      try {
        const history = loadHistory();
        const response = await fetch(`${API_URL}/api/v1/suggestions`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ history }),
        });

        if (response.ok) {
          const data = await response.json();
          setSuggestions(data.suggestions);
        }
      } catch (error) {
        console.error("Failed to fetch suggestions:", error);
      } finally {
        setLoadingSuggestions(false);
      }
    }
    fetchSuggestions();
  }, []);

  // Save threads when changed
  useEffect(() => {
    if (threads.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(threads));
    }
  }, [threads]);

  // Scroll to bottom helper
  const scrollToBottom = (behavior: ScrollBehavior = "smooth") => {
    messagesEndRef.current?.scrollIntoView({ behavior });
  };

  useEffect(() => {
    scrollToBottom();
  }, [state.currentAnswer, state.status, currentThreadId]);

  const createNewThread = () => {
    setCurrentThreadId(null);
    setState({ status: "idle", currentAnswer: "" });
    setShowSidebar(false);
  };

  const handleDownload = (content: string, id: string) => {
    const blob = new Blob([content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `searchflow-${id.slice(0, 8)}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;

    saveHistory(query);
    setState({ status: "searching", currentAnswer: "" });
    setStatusMessage("Searching the web...");

    // Create thread if needed
    let threadId = currentThreadId;
    let newThreads = [...threads];

    if (!threadId) {
      const newThread: ChatThread = {
        id: generateId(),
        title: query.length > 30 ? query.substring(0, 30) + "..." : query,
        messages: [],
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };
      newThreads = [newThread, ...threads];
      threadId = newThread.id;
      setThreads(newThreads);
      setCurrentThreadId(threadId);
    }

    // Add User Message
    const userMsg: Message = {
      id: generateId(),
      role: "user",
      content: query,
      timestamp: Date.now(),
    };

    // Update thread with user message
    const updatedThreads = newThreads.map(t => {
      if (t.id === threadId) {
        return {
          ...t,
          messages: [...t.messages, userMsg],
          updatedAt: Date.now(),
          title: t.messages.length === 0 ? (query.length > 30 ? query.substring(0, 30) + "..." : query) : t.title
        };
      }
      return t;
    });
    setThreads(updatedThreads);

    // Start Search
    try {
      const response = await fetch(`${API_URL}/api/v1/search/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) throw new Error("No response body");

      let buffer = "";
      let fullAnswer = "";
      let sources: string[] = [];
      let context: Source[] = [];
      let confidence = 0;
      let modelUsed = "";

      setState({ status: "streaming", currentAnswer: "" });
      setStatusMessage("Analyzing results...");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
            const trimmed = line.replace(/^data: /, "").trim();
            if (!trimmed || trimmed === "[DONE]") continue;

            try {
              const event = JSON.parse(trimmed);

              if (event.status) {
                setStatusMessage(event.status);
              }

              if (event.answer) {
                fullAnswer += event.answer;
                setState(prev => ({ ...prev, currentAnswer: fullAnswer }));
              }

              if (event.sources) sources = event.sources;
              if (event.context) context = event.context;
              if (event.confidence) confidence = event.confidence;
              if (event.model_used) modelUsed = event.model_used;

            } catch (e) {
              console.warn("Parse error:", e);
            }
        }
      }

      // Finalize Assistant Message
      const assistantMsg: Message = {
        id: generateId(),
        role: "assistant",
        content: fullAnswer,
        sources,
        context,
        confidence,
        model_used: modelUsed,
        timestamp: Date.now(),
      };

      setThreads(prev => prev.map(t => {
        if (t.id === threadId) {
          return {
            ...t,
            messages: [...t.messages, assistantMsg],
            updatedAt: Date.now()
          };
        }
        return t;
      }));

      setState({ status: "done", currentAnswer: fullAnswer });
      if (modelUsed) setLastModelUsed(modelUsed);

    } catch (error) {
      console.error("Search failed:", error);
      setState({
        status: "error",
        currentAnswer: "",
        error: error instanceof Error ? error.message : "Search failed"
      });

      // Add error message to chat
      const errorMsg: Message = {
        id: generateId(),
        role: "assistant",
        content: `**Error:** ${error instanceof Error ? error.message : "Search failed. Please try again."}`,
        timestamp: Date.now(),
      };

      setThreads(prev => prev.map(t => {
        if (t.id === threadId) {
          return {
            ...t,
            messages: [...t.messages, errorMsg],
            updatedAt: Date.now()
          };
        }
        return t;
      }));
    }
  };

  const currentThread = threads.find((t) => t.id === currentThreadId);

  return (
    <div className="flex h-screen bg-[var(--background)] text-[var(--foreground)] transition-colors duration-300 overflow-hidden font-sans">

      {/* Sidebar - Collapsible on mobile */}
      <AppSidebar
        threads={threads}
        currentThreadId={currentThreadId}
        onSelectThread={setCurrentThreadId}
        onNewChat={createNewThread}
        isOpen={showSidebar}
        onClose={() => setShowSidebar(false)}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full relative transition-all duration-300">

        {/* Header (Top Bar) */}
        <AppHeader
          onToggleSidebar={() => setShowSidebar(!showSidebar)}
          onOpenSettings={() => setShowSettings(true)}
          lastModelUsed={lastModelUsed}
        />

        {/* Scrollable Chat Area */}
        <div className="flex-1 overflow-y-auto w-full scrollbar-thin scrollbar-thumb-[var(--border)] scrollbar-track-transparent">
          <ChatArea
            currentThread={currentThread}
            state={state}
            statusMessage={statusMessage}
            onDownload={handleDownload}
            messagesEndRef={messagesEndRef}
            suggestions={suggestions}
            isLoadingSuggestions={loadingSuggestions}
            onSearch={handleSearch}
          />
        </div>

        {/* Fixed Input Area */}
        <InputArea
          onSearch={handleSearch}
          isLoading={state.status === "searching" || state.status === "streaming"}
        />

        {/* Modals */}
        <SettingsModal
          isOpen={showSettings}
          onClose={() => setShowSettings(false)}
          currentModel={lastModelUsed}
        />
      </main>
    </div>
  );
}
