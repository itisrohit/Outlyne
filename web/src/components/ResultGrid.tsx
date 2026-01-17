import { AnimatePresence, motion } from "framer-motion";
import { ExternalLink, Info } from "lucide-react";

export interface SearchResult {
  title: string;
  url: string;
  thumbnail: string;
  similarity_score: number;
}

interface ResultGridProps {
  results: SearchResult[];
  isLoading: boolean;
}

export function ResultGrid({ results, isLoading }: ResultGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 w-full">
        {Array.from({ length: 12 }).map((_, i) => (
          <div
            // biome-ignore lint/suspicious/noArrayIndexKey: skeleton items
            key={`skeleton-${i}`}
            className="aspect-square glass rounded-2xl animate-pulse bg-white/5"
          />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 w-full">
      <AnimatePresence mode="popLayout">
        {results.map((result) => (
          <motion.div
            key={`${result.url}-${result.similarity_score}`}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.2 }}
            className="group relative aspect-square glass rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all"
          >
            <img
              src={result.thumbnail}
              alt={result.title}
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
              loading="lazy"
            />

            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

            <div className="absolute bottom-3 left-3 right-3 translate-y-4 group-hover:translate-y-0 opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-center justify-between">
              <p className="text-white text-xs font-medium truncate pr-2 flex-1">{result.title}</p>
              <a
                href={result.url}
                target="_blank"
                rel="noreferrer"
                className="p-1.5 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors"
                title="View Source"
              >
                <ExternalLink size={14} />
              </a>
            </div>

            <div className="absolute top-3 right-3 px-2 py-1 bg-black/50 backdrop-blur-md rounded-full border border-white/10 text-[10px] font-bold text-white/90 opacity-0 group-hover:opacity-100 transition-opacity">
              {Math.round(result.similarity_score * 100)}% Match
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {!isLoading && results.length === 0 && (
        <div className="col-span-full py-20 text-center">
          <Info className="w-8 h-8 text-zinc-600 mx-auto mb-4" />
          <p className="text-zinc-500 font-medium italic">
            No results found yet. Try drawing something!
          </p>
        </div>
      )}
    </div>
  );
}
