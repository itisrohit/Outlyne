import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, Cpu, Flame, Loader2, Palette, Search, Zap } from "lucide-react";
import { useCallback, useState } from "react";
import { DrawingCanvas } from "./components/DrawingCanvas";
import { ResultGrid, type SearchResult } from "./components/ResultGrid";
import { cn } from "./utils/cn";

function App() {
  const [sketch, setSketch] = useState<string>("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const performSearch = useCallback(async () => {
    // We only need the sketch to start
    if (!sketch) return;

    setIsLoading(true);
    setHasSearched(true);

    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sketch_base64: sketch,
          query: "", // Pure sketch search: context is inferred by backend
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
  }, [sketch]);

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
            <div className="bg-zinc-900/40 p-6 rounded-3xl border border-white/5 backdrop-blur-xl shadow-2xl space-y-6">
              <section className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-bold uppercase tracking-widest text-zinc-500 flex items-center gap-2">
                    <Palette size={12} className="text-indigo-500" />
                    Input Canvas
                  </div>
                  <div className="flex items-center gap-1.5">
                    {isLoading ? (
                      <span className="flex items-center gap-1.5 text-[10px] font-bold text-indigo-400 animate-pulse">
                        <Loader2 size={10} className="animate-spin" />
                        Processing Vision
                      </span>
                    ) : (
                      <span className="text-[10px] text-zinc-600 font-mono">224px IR Mode</span>
                    )}
                  </div>
                </div>
                <DrawingCanvas onExport={setSketch} />
              </section>

              <button
                type="button"
                onClick={performSearch}
                disabled={isLoading || !sketch}
                className={cn(
                  "w-full py-4 rounded-2xl font-black text-xs uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-3 overflow-hidden relative group",
                  sketch && !isLoading
                    ? "bg-indigo-600 text-white shadow-xl shadow-indigo-600/20 hover:bg-indigo-500 active:scale-[0.98]"
                    : "bg-zinc-800 text-zinc-500 cursor-not-allowed border border-white/5",
                )}
              >
                {isLoading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <span>Search Marketplace</span>
                    <ArrowRight
                      size={16}
                      className="group-hover:translate-x-1 transition-transform"
                    />
                  </>
                )}
              </button>
            </div>

            <div className="px-5 py-4 bg-white/[0.02] border border-white/5 rounded-2xl">
              <p className="text-[10px] leading-relaxed text-zinc-500 font-medium">
                <span className="text-indigo-400 font-bold uppercase mr-1">Pro Tip:</span>
                Our Vision Core automatically detects the category from your sketch. Just draw and
                search.
              </p>
            </div>
          </aside>

          {/* Right Column: Results */}
          <section className="min-h-[600px] flex flex-col">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-xl font-bold flex items-center gap-3 uppercase tracking-tight">
                Market Results
                {results.length > 0 && (
                  <span className="text-[10px] bg-white/5 border border-white/10 px-2 py-0.5 rounded text-zinc-400 font-mono">
                    {results.length} Found
                  </span>
                )}
              </h2>

              {isLoading && (
                <div className="flex items-center gap-2 px-3 py-1 bg-indigo-500/10 rounded-full border border-indigo-500/20">
                  <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-ping" />
                  <span className="text-[10px] font-black text-indigo-400 uppercase tracking-tighter">
                    Ranking Candidates
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
                  <h3 className="text-3xl font-black mb-4 tracking-tight">Visual Discovery</h3>
                  <p className="text-zinc-500 max-w-sm mx-auto leading-relaxed text-sm">
                    Draw your concept on the left and hit search. <br />
                    AI will interpret your lines and find matching internet imagery.
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
    <div className="flex items-center gap-1.5 grayscale opacity-70 hover:grayscale-0 hover:opacity-100 transition-all cursor-default text-zinc-400">
      <div
        className={cn(
          "p-1 rounded-md text-white",
          color === "indigo" ? "bg-indigo-500" : "bg-purple-500",
        )}
      >
        {icon}
      </div>
      <span className="text-[10px] font-bold uppercase tracking-tight">{label}</span>
    </div>
  );
}

export default App;
