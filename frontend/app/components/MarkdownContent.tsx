"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CodeBlock } from "./CodeBlock";
import type { Source } from "./SourceCard";

interface MarkdownContentProps {
  content: string;
  sources?: Source[];
}

// Process citations: [0], [1], etc. -> clickable links
function processCitations(content: string, sources: Source[]): string {
  return content.replace(/\[(\d+)\]/g, (match, index) => {
    const idx = parseInt(index, 10);
    if (sources && sources[idx] && sources[idx].url) {
      return `[<sup>${idx}</sup>](${sources[idx].url})`;
    }
    return `<sup>[${idx}]</sup>`;
  });
}

export function MarkdownContent({ content, sources = [] }: MarkdownContentProps) {
  const processedContent =
    sources.length > 0 ? processCitations(content, sources) : content;

  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ className, children }) {
          const isInline = !className;
          if (isInline) {
            return (
              <code className="px-1.5 py-0.5 bg-zinc-800 text-blue-300 rounded text-sm font-mono border border-zinc-700/50">
                {children}
              </code>
            );
          }
          return <CodeBlock className={className}>{children}</CodeBlock>;
        },
        h1: ({ children }) => (
          <h1 className="text-2xl font-bold text-zinc-100 mt-8 mb-4">
            {children}
          </h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-xl font-semibold text-zinc-200 mt-6 mb-3">
            {children}
          </h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-lg font-semibold text-zinc-300 mt-5 mb-2">
            {children}
          </h3>
        ),
        p: ({ children }) => (
          <p className="text-zinc-300 leading-7 mb-4 text-base">{children}</p>
        ),
        ul: ({ children }) => (
          <ul className="list-disc list-outside ml-5 text-zinc-300 mb-4 space-y-1">
            {children}
          </ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal list-outside ml-5 text-zinc-300 mb-4 space-y-1">
            {children}
          </ol>
        ),
        a: ({ href, children }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:text-blue-300 underline decoration-blue-400/30 hover:decoration-blue-300/60 transition-colors"
          >
            {children}
          </a>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-zinc-700 pl-4 py-1 italic text-zinc-400 my-4 bg-zinc-900/30 rounded-r">
            {children}
          </blockquote>
        ),
        table: ({ children }) => (
          <div className="overflow-x-auto my-6 rounded-lg border border-zinc-800">
            <table className="w-full text-left text-sm">{children}</table>
          </div>
        ),
        thead: ({ children }) => (
          <thead className="bg-zinc-900 text-zinc-200 uppercase font-medium">
            {children}
          </thead>
        ),
        th: ({ children }) => (
          <th className="px-4 py-3 border-b border-zinc-800">{children}</th>
        ),
        td: ({ children }) => (
          <td className="px-4 py-3 border-b border-zinc-800/50 text-zinc-400">
            {children}
          </td>
        ),
      }}
    >
      {processedContent}
    </ReactMarkdown>
  );
}
