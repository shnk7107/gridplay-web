import React from "react";
import TelemetryExplorer from "./components/TelemetryExplorer";
import PredictionKit from "./components/PredictionKit";
import StrategyPlayground from "./components/StrategyPlayground";
import FanBattle from "./components/FanBattle";

export default function App(){
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <header className="max-w-6xl mx-auto mb-6">
        <h1 className="text-3xl font-bold">GridPlay — Telemetry & Strategy</h1>
        <p className="text-sm text-gray-600">Explore telemetry, simulate strategies, and battle the AI.</p>
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-1 gap-6">
        <TelemetryExplorer />
        <PredictionKit />
        <StrategyPlayground />
        <FanBattle />
      </main>
    </div>
  );
}
