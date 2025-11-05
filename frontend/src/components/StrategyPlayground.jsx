import React, { useState } from "react";

export default function StrategyPlayground() {
  const [pitLap, setPitLap] = useState(25);
  const [tyre, setTyre] = useState("medium");

  const simulate = () => {
    alert(`Simulated strategy: pit at lap ${pitLap} → switch to ${tyre}. (Stub)`);
  };

  return (
    <section className="bg-white rounded p-4 shadow">
      <h2 className="text-xl font-semibold mb-2">Strategy Playground</h2>
      <div className="flex gap-3 items-center">
        <label>Pit lap</label>
        <input
          type="number"
          value={pitLap}
          onChange={(e) => setPitLap(Number(e.target.value))}
          className="border p-1 w-24"
        />
        <select value={tyre} onChange={(e) => setTyre(e.target.value)} className="border p-1">
          <option value="soft">Soft</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
        <button onClick={simulate} className="px-3 py-1 bg-green-600 text-white rounded">
          Simulate
        </button>
      </div>
      <p className="mt-3 text-sm text-gray-600">
        Note: this is a local simulation UI. Hook it to a backend simulation endpoint for real strategy outputs.
      </p>
    </section>
  );
}
