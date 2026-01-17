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
            className="aspect-square bg-black/5 rounded-[1.5rem] animate-pulse"
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
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.6, ease: [0.2, 0.8, 0.2, 1] }}
            className="group relative aspect-square bg-[#fcfcfc] rounded-[1.5rem] overflow-hidden shadow-[0_15px_40px_-10px_rgba(0,0,0,0.08)] border border-black/5 hover:shadow-[0_20px_50px_-15px_rgba(0,0,0,0.12)] transition-all duration-700"
          >
            <img
              src={result.thumbnail}
              alt={result.title}
              className="w-full h-full object-cover grayscale-[0.1] group-hover:grayscale-0 group-hover:scale-110 transition-all duration-1000 ease-out"
              loading="lazy"
            />

            <div className="absolute inset-0 bg-white/0 group-hover:bg-white/10 transition-colors duration-500" />

            <div className="absolute bottom-6 left-6 right-6 translate-y-2 group-hover:translate-y-0 opacity-0 group-hover:opacity-100 transition-all duration-500 flex items-center justify-between z-10">
              <span className="text-black text-[12px] font-bold tracking-tight bg-white/90 backdrop-blur-md px-3 py-1 rounded-full shadow-lg truncate flex-1 mr-3">
                {result.title}
              </span>
              <a
                href={result.url}
                target="_blank"
                rel="noreferrer"
                className="p-2.5 bg-black text-white hover:bg-[#8fb19e] rounded-full transition-all duration-300 shadow-xl"
              >
                <ExternalLink size={12} />
              </a>
            </div>

            <div className="absolute top-6 right-6 px-3 py-1 bg-white/90 backdrop-blur-md text-black rounded-full text-[10px] font-black tracking-widest uppercase opacity-0 group-hover:opacity-100 transition-opacity duration-300 shadow-lg">
              {Math.round(result.similarity_score * 100)}%
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {!isLoading && results.length === 0 && (
        <div className="col-span-full py-40 text-center opacity-20">
          <Info className="w-8 h-8 text-black mx-auto mb-6" />
          <p className="text-[11px] uppercase tracking-[0.6em] font-black text-black">Silence</p>
        </div>
      )}
    </div>
  );
}
