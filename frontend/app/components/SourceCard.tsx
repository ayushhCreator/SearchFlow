"use client";


export interface Source {
  title: string;
  url: string;
  source: string;
  text: string;
  credibility_score?: number;
  credibility_category?: string;
}

function getFavicon(url: string) {
  try {
    const domain = new URL(url).hostname;
    return `https://www.google.com/s2/favicons?domain=${domain}&sz=32`;
  } catch {
    return "/globe.svg";
  }
}

function getDomain(url: string) {
  try {
    return new URL(url).hostname.replace("www.", "");
  } catch {
    return url;
  }
}

interface SourceCardProps {
  source: Source;
}

export function SourceCard({ source }: SourceCardProps) {
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex flex-col justify-between p-3 bg-zinc-900 border border-zinc-800 rounded-lg hover:bg-zinc-800 hover:border-zinc-700 transition-all group h-full"
    >
      <div className="flex items-center gap-2 mb-2">
        <img
          src={getFavicon(source.url)}
          alt=""
          className="w-4 h-4 rounded-sm opacity-70 group-hover:opacity-100"
          onError={(e) => (e.currentTarget.style.display = "none")}
        />
        <span className="text-xs text-zinc-500 font-medium truncate group-hover:text-zinc-400">
          {getDomain(source.url)}
        </span>
        {source.credibility_score && (
          <span
            className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
              source.credibility_score >= 0.8
                ? "bg-green-500/10 text-green-400"
                : source.credibility_score >= 0.6
                ? "bg-yellow-500/10 text-yellow-400"
                : "bg-zinc-500/10 text-zinc-400"
            }`}
          >
            {Math.round(source.credibility_score * 100)}%
          </span>
        )}
      </div>
      <h4 className="text-sm text-zinc-300 font-medium leading-tight line-clamp-2 group-hover:text-blue-400">
        {source.title || source.text.slice(0, 50)}
      </h4>
    </a>
  );
}
