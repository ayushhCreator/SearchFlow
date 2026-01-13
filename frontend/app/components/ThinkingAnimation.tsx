"use client";


interface ThinkingAnimationProps {
  message: string;
}

export function ThinkingAnimation({ message }: ThinkingAnimationProps) {
  return (
    <div className="flex items-center gap-3 text-zinc-400">
      <div className="flex items-center gap-1">
        <div
          className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
          style={{ animationDelay: "0ms" }}
        />
        <div
          className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
          style={{ animationDelay: "150ms" }}
        />
        <div
          className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
          style={{ animationDelay: "300ms" }}
        />
      </div>
      <span className="text-sm font-medium">{message}</span>
    </div>
  );
}
