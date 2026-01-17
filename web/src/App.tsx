import { motion } from "framer-motion";
import { Palette, Search, Zap } from "lucide-react";

function App() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-2xl w-full text-center space-y-8"
      >
        <div className="space-y-4">
          <h1 className="text-6xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
            Outlyne
          </h1>
          <p className="text-zinc-400 text-xl font-medium">
            Real-time visual intelligence meets live internet recall.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <FeatureCard
            icon={<Palette className="w-5 h-5 text-indigo-400" />}
            title="Sketch"
            description="Draw anything on the canvas"
          />
          <FeatureCard
            icon={<Zap className="w-5 h-5 text-purple-400" />}
            title="Search"
            description="Instant visual embedding"
          />
          <FeatureCard
            icon={<Search className="w-5 h-5 text-pink-400" />}
            title="Recall"
            description="Live internet re-ranking"
          />
        </div>

        <button
          type="button"
          className="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 transition-colors rounded-full font-bold text-lg shadow-xl shadow-indigo-500/20 active:scale-95"
        >
          Get Started
        </button>
      </motion.div>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="glass p-6 rounded-2xl text-left space-y-3 hover:border-white/20 transition-colors group cursor-default">
      <div className="p-2 bg-white/5 w-fit rounded-lg group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <div>
        <h3 className="font-bold text-lg">{title}</h3>
        <p className="text-sm text-zinc-500 leading-relaxed">{description}</p>
      </div>
    </div>
  );
}

export default App;
