import { ArrowRight, Loader2, Palette } from "lucide-react";
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
    if (!sketch) return;
    setIsLoading(true);
    setHasSearched(true);

    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sketch_base64: sketch,
          query: "",
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
    <div className="h-screen bg-[#fcfcfc] text-[#2d3436] selection:bg-[#8fb19e]/20 selection:text-black flex flex-col overflow-hidden">
      {/* Subtle Texture */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] bg-[url('https://www.transparenttextures.com/patterns/notebook.png')]" />

      <main className="relative z-10 flex-1 flex flex-col max-w-[1600px] mx-auto w-full px-10 pt-10 pb-6 animate-organic overflow-hidden">
        {/* Compact Technical Header */}
        <header className="flex items-end justify-between gap-12 mb-6 pb-5 border-b border-black/5">
          <div className="flex flex-col justify-end">
            <h1 className="text-3xl font-light tracking-tight font-serif text-[#2d3436] flex items-center gap-2 leading-none mb-1.5">
              Outlyne
              <div className="h-1.5 w-1.5 rounded-full bg-[#8fb19e] shadow-[0_0_10px_#8fb19e]" />
            </h1>
            <p className="text-[9px] uppercase tracking-[0.4em] font-medium text-black/30 pl-0.5 leading-none">
              {"// Natural Vision Protocol"}
            </p>
          </div>

          <div className="flex items-center gap-8 text-[#2d3436]">
            <div className="flex flex-col items-end gap-0.5">
              <span className="text-[8px] uppercase tracking-[0.2em] font-bold text-black/20 leading-none">
                {"Version"}
              </span>
              <span className="text-[10px] font-medium tracking-[0.15em] uppercase leading-none">
                {"Vision.02"}
              </span>
            </div>
            <div className="w-px h-6 bg-black/5 rotate-12" />
            <div className="flex flex-col items-end gap-0.5">
              <span className="text-[8px] uppercase tracking-[0.2em] font-bold text-black/20 leading-none">
                {"Engine"}
              </span>
              <span className="text-[10px] font-medium tracking-[0.15em] uppercase leading-none">
                {"Muted Core"}
              </span>
            </div>
          </div>
        </header>

        <div className="flex-1 min-h-0 grid lg:grid-cols-[340px_1fr] gap-16 items-stretch">
          {/* Input Area - Fixed height side */}
          <aside className="space-y-8 flex flex-col py-2">
            <section className="space-y-5">
              <div className="flex items-center justify-between px-1">
                <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-black/30 flex items-center gap-2">
                  <Palette size={12} className="text-[#8fb19e]" />
                  Intent Space
                </h3>
              </div>

              <DrawingCanvas onExport={setSketch} className="zen-surface rounded-[2rem] p-1.5" />
            </section>

            <button
              type="button"
              onClick={performSearch}
              disabled={isLoading || !sketch}
              className={cn(
                "w-full py-5 rounded-full font-black text-[11px] uppercase tracking-[0.4em] transition-all duration-500 relative overflow-hidden group border-none",
                sketch && !isLoading
                  ? "bg-[#2d3436] text-white shadow-xl shadow-black/5 hover:bg-black active:scale-[0.98]"
                  : "bg-black/5 text-black/10 cursor-not-allowed",
              )}
            >
              <div className="relative z-10 flex items-center justify-center gap-4">
                {isLoading ? (
                  <>
                    <Loader2 size={14} className="animate-spin" />
                    <span>{"Distilling"}</span>
                  </>
                ) : (
                  <>
                    <span>{"Recall Intent"}</span>
                    <ArrowRight
                      size={14}
                      className="group-hover:translate-x-2 transition-transform duration-500"
                    />
                  </>
                )}
              </div>
            </button>

            <div className="mt-auto hidden lg:block opacity-60">
              <p className="text-[9px] text-black/30 leading-relaxed font-medium uppercase tracking-widest px-1">
                {"The engine interprets your marks as universal semantic intent."}
              </p>
            </div>
          </aside>

          {/* Results Area - Independently scrollable */}
          <section className="flex flex-col min-h-0">
            <div className="flex items-center justify-between mb-8 px-1">
              <h2 className="text-[10px] font-black uppercase tracking-[0.4em] text-black/30">
                Visual Archetypes
                {results.length > 0 && (
                  <span className="ml-4 font-normal text-black/20">
                    / {results.length} recall results
                  </span>
                )}
              </h2>
            </div>

            <div
              className={cn(
                "flex-1 px-2 -mx-2 pb-12 scrollbar-zen",
                results.length > 0 ? "overflow-y-auto" : "overflow-hidden",
              )}
            >
              <ResultGrid results={results} isLoading={isLoading && results.length === 0} />

              {!hasSearched && (
                <div className="h-full flex flex-col items-center justify-center text-center opacity-30 py-12">
                  <div className="w-px h-16 bg-gradient-to-b from-black/10 to-transparent mb-8" />
                  <h3 className="text-lg font-light text-[#2d3436] tracking-tight max-w-sm leading-relaxed serif italic">
                    {"Project your concept to begin recall."}
                  </h3>
                </div>
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;
