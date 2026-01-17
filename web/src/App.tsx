import { AnimatePresence, motion } from "framer-motion";
import { Command, Cpu, Flame, Loader2, Palette, Search, Sparkles, Zap } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { DrawingCanvas } from "./components/DrawingCanvas";
import { ResultGrid, type SearchResult } from "./components/ResultGrid";
import { cn } from "./utils/cn";

function App() {
  const [query, setQuery] = useState("");
  const [sketch, setSketch] = useState<string>("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  // Track search state
  const lastSearchRef = useRef<string>("");
  const debounceTimer = useRef<Timer | null>(null);

  const performSearch = useCallback(async (currentSketch: string, currentQuery: string) => {
    // We need both to perform a meaningful internet recall
    if (!currentSketch || !currentQuery || currentQuery.length < 2) return;

    // Avoid redundant searches
    const searchId = currentSketch.slice(-50) + currentQuery;
    if (lastSearchRef.current === searchId) return;
    lastSearchRef.current = searchId;

    setIsLoading(true);
    setHasSearched(true);

    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sketch_base64: currentSketch,
          query: currentQuery,
          max_results: 12,
        }),
      });

      if (!response.ok) throw new Error("Search failed");

      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Live Sync Logic: Trigger search when sketch or query changes
  useEffect(() => {
    if (debounceTimer.current) clearTimeout(debounceTimer.current);

    debounceTimer.current = setTimeout(() => {
      performSearch(sketch, query);
    }, 600); // 600ms debounce for live draw feel

    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, [sketch, query, performSearch]);

  return (
    <div className="min-h-screen bg-zinc-950 font-sans text-zinc-50 overflow-x-hidden">
      {/* Background Gradients */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/10 blur-[120px] rounded-full" />
      </div>

      <main className="relative z-10 max-w-7xl mx-auto px-4 py-8 lg:py-12">
        {/* Header */}
        <header className="flex flex-col md:flex-row items-center justify-between gap-6 mb-12">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-600/30">
              <Zap className="w-6 h-6 text-white fill-white" />
            </div>
            <div>
              <h1 className="text-3xl font-black tracking-tight leading-none italic uppercase">
                Outlyne
              </h1>
              <p className="text-[10px] uppercase tracking-widest font-bold text-zinc-500 mt-1">
                Visual Intelligence Engine
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 bg-zinc-900/50 backdrop-blur-md px-4 py-2 rounded-full border border-white/5">
            <StatusBadge icon={<Cpu size={12} />} label="SigLIP2" color="indigo" />
            <StatusBadge icon={<Flame size={12} />} label="OpenVINO" color="purple" />
          </div>
        </header>

        <div className="grid lg:grid-cols-[450px_1fr] gap-12 items-start">
          {/* Left Column: Input */}
          <aside className="space-y-6 sticky top-12">
            <div className="bg-zinc-900/40 p-6 rounded-3xl border border-white/5 backdrop-blur-xl shadow-2xl">
              <section className="space-y-4 mb-6">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-bold uppercase tracking-widest text-zinc-500 flex items-center gap-2">
                    <Palette size={12} className="text-indigo-500" />
                    Live Canvas
                  </div>
                  <div className="flex items-center gap-1.5">
                    {isLoading ? (
                      <span className="flex items-center gap-1.5 text-[10px] font-bold text-indigo-400 animate-pulse">
                        <Loader2 size={10} className="animate-spin" />
                        Scanning Web
                      </span>
                    ) : (
                      <span className="text-[10px] text-zinc-600 font-mono">Ready</span>
                    )}
                  </div>
                </div>
                <DrawingCanvas onExport={setSketch} />
              </section>

              <section className="space-y-3">
                <div className="flex items-center justify-between">
                  <label
                    htmlFor="context-query"
                    className="text-xs font-bold uppercase tracking-widest text-zinc-500 flex items-center gap-2"
                  >
                    <Search size={12} className="text-indigo-500" />
                    Visual Context
                  </label>
                  {!query && (
                    <span className="text-[10px] text-orange-500/70 font-bold uppercase animate-pulse">
                      Required
                    </span>
                  )}
                </div>
                <div className="relative group">
                  <input
                    id="context-query"
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g. industrial chair, mountain landscape"
                    className="w-full bg-zinc-950/50 border border-white/5 rounded-xl px-4 py-3 focus:outline-none focus:ring-1 focus:ring-indigo-500/50 focus:bg-zinc-950 transition-all text-sm group-hover:border-white/10"
                  />
                </div>
              </section>

              <div className="mt-6 pt-6 border-t border-white/5 space-y-3">
                <div className="flex items-center gap-3 text-zinc-500">
                  <div className="p-1.5 bg-zinc-800 rounded-lg">
                    <Sparkles size={14} className="text-indigo-400" />
                  </div>
                  <p className="text-[11px] leading-snug">
                    <span className="text-zinc-300 font-bold">Concept Search:</span> Hint the engine
                    with keywords, then draw to refine results.
                  </p>
                </div>
              </div>
            </div>

            <div className="px-4 py-3 bg-indigo-500/5 border border-indigo-500/10 rounded-2xl flex items-center gap-3">
              <Command size={14} className="text-indigo-400" />
              <p className="text-[10px] text-indigo-300/60 font-medium">
                Engine synchronizes visual intent every{" "}
                <span className="text-indigo-300">600ms</span>
              </p>
            </div>
          </aside>

          {/* Right Column: Results */}
          <section className="min-h-[600px] flex flex-col">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-xl font-bold flex items-center gap-3 uppercase tracking-tight">
                Live Stream
                {results.length > 0 && (
                  <span className="text-[10px] bg-white/5 border border-white/10 px-2 py-0.5 rounded text-zinc-400 font-mono">
                    {results.length} Matches
                  </span>
                )}
              </h2>

              {isLoading && (
                <div className="flex items-center gap-2 px-3 py-1 bg-indigo-500/10 rounded-full border border-indigo-500/20">
                  <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-ping" />
                  <span className="text-[10px] font-black text-indigo-400 uppercase tracking-tighter">
                    Real-time Ranking
                  </span>
                </div>
              )}
            </div>

            <ResultGrid results={results} isLoading={isLoading && results.length === 0} />

            {!hasSearched && (
              <AnimatePresence>
                <motion.div
                  key="empty-state"
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex-1 flex flex-col items-center justify-center text-center p-12 glass rounded-[2.5rem] border-white/5"
                >
                  <div className="relative mb-8">
                    <div className="absolute inset-0 bg-indigo-500/20 blur-3xl rounded-full" />
                    <div className="relative p-6 bg-zinc-900 rounded-3xl border border-white/10 shadow-2xl">
                      <Search className="w-12 h-12 text-indigo-500" />
                    </div>
                  </div>
                  <h3 className="text-3xl font-black mb-4 tracking-tight">Awaiting Vision</h3>
                  <p className="text-zinc-500 max-w-sm mx-auto leading-relaxed text-sm">
                    Enter a context hint above and start drawing. <br />
                    Outlyne will search the internet for your sketch in real-time.
                  </p>
                </motion.div>
              </AnimatePresence>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

function StatusBadge({
  icon,
  label,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  color: "indigo" | "purple";
}) {
  return (
    <div className="flex items-center gap-1.5 grayscale opacity-70 hover:grayscale-0 hover:opacity-100 transition-all cursor-default">
      <div
        className={cn(
          "p-1 rounded-md text-white",
          color === "indigo" ? "bg-indigo-500" : "bg-purple-500",
        )}
      >
        {icon}
      </div>
      <span className="text-[10px] font-bold uppercase tracking-tight text-zinc-400">{label}</span>
    </div>
  );
}

export default App;
