"use client";

import React, { useState } from "react";

interface CodeBlockProps {
  className?: string;
  children: React.ReactNode;
}

export function CodeBlock({ className, children }: CodeBlockProps) {
  const language = className?.replace("language-", "") || "text";
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const code = String(children).replace(/\n$/, "");
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative my-4 rounded-lg overflow-hidden group bg-zinc-950/50 border border-zinc-800">
      <div className="flex items-center justify-between px-4 py-2 bg-zinc-900/50 border-b border-zinc-800">
        <span className="text-xs text-zinc-500 font-mono uppercase">
          {language}
        </span>
        <button
          onClick={handleCopy}
          className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
      <pre className="p-4 overflow-x-auto">
        <code className={`text-sm font-mono text-zinc-300 ${className || ""}`}>
          {children}
        </code>
      </pre>
    </div>
  );
}
