import { Download, Eraser, Pencil, RotateCcw } from "lucide-react";
import type React from "react";
import { useEffect, useRef, useState } from "react";
import { cn } from "../utils/cn";

interface DrawingCanvasProps {
  onExport: (base64: string) => void;
  className?: string;
}

export function DrawingCanvas({ onExport, className }: DrawingCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [tool, setTool] = useState<"pencil" | "eraser">("pencil");
  const brushSize = 4;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Set white background initially
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Set default drawing settings
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.strokeStyle = "#000000"; // Always black on white for the model
    ctx.lineWidth = brushSize;
  }, []);

  const startDrawing = (e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const { x, y } = getCoordinates(e);
    ctx.beginPath();
    ctx.moveTo(x, y);
    setIsDrawing(true);
  };

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const { x, y } = getCoordinates(e);

    // Model expects black strokes on white background
    ctx.strokeStyle = tool === "eraser" ? "#ffffff" : "#000000";
    ctx.lineWidth = tool === "eraser" ? brushSize * 4 : brushSize;

    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const stopDrawing = () => {
    if (!isDrawing) return;
    setIsDrawing(false);
    exportCanvas();
  };

  const getCoordinates = (e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    if ("touches" in e && e.touches[0]) {
      return {
        x: (e.touches[0].clientX - rect.left) * scaleX,
        y: (e.touches[0].clientY - rect.top) * scaleY,
      };
    }

    const mouseEvent = e as React.MouseEvent;
    return {
      x: (mouseEvent.clientX - rect.left) * scaleX,
      y: (mouseEvent.clientY - rect.top) * scaleY,
    };
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    exportCanvas();
  };

  const exportCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Send only the data part of the base64 string
    const base64 = canvas.toDataURL("image/png");
    onExport(base64.split(",")[1] ?? "");
  };

  return (
    <div className={cn("flex flex-col gap-4", className)}>
      <div className="flex items-center justify-between bg-zinc-900/50 p-2 rounded-xl border border-white/5 backdrop-blur-md">
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setTool("pencil")}
            className={cn(
              "p-2 rounded-lg transition-all active:scale-90",
              tool === "pencil"
                ? "bg-indigo-500 text-white shadow-lg shadow-indigo-500/20"
                : "hover:bg-white/5 text-zinc-400",
            )}
            title="Pencil"
          >
            <Pencil size={20} />
          </button>
          <button
            type="button"
            onClick={() => setTool("eraser")}
            className={cn(
              "p-2 rounded-lg transition-all active:scale-90",
              tool === "eraser"
                ? "bg-indigo-500 text-white shadow-lg shadow-indigo-500/20"
                : "hover:bg-white/5 text-zinc-400",
            )}
            title="Eraser"
          >
            <Eraser size={20} />
          </button>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={clearCanvas}
            className="p-2 rounded-lg hover:bg-white/5 text-zinc-400 transition-all active:rotate-[-45deg]"
            title="Clear Canvas"
          >
            <RotateCcw size={20} />
          </button>
          <button
            type="button"
            onClick={exportCanvas}
            className="p-2 rounded-lg hover:bg-white/5 text-zinc-400"
            title="Export"
          >
            <Download size={20} />
          </button>
        </div>
      </div>

      <div className="relative group aspect-square bg-white rounded-2xl overflow-hidden shadow-2xl border-4 border-zinc-900">
        <canvas
          ref={canvasRef}
          width={448} // 224 * 2 (Super-sampled)
          height={448}
          className="w-full h-full cursor-crosshair touch-none"
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
        />
        <div className="absolute inset-0 pointer-events-none border-2 border-indigo-500/0 group-hover:border-indigo-500/20 transition-colors" />
      </div>
    </div>
  );
}
