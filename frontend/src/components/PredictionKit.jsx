// frontend/src/components/PredictionKit.jsx
import React, { useState } from "react";
import { postPredict } from "../api";

export default function PredictionKit() {
  const [qualMap, setQualMap] = useState({ VER: 1, LEC: 2 });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const payload = { race_id: "2023-01-bahrain", qualifying_pos: qualMap };
      const res = await postPredict(payload);
      setResult(res);
    } catch (err) {
      console.error(err);
      setError("Prediction failed. Check backend logs.");
    } finally {
      setLoading(false);
    }
  };

  // convert result.predictions -> sorted array [{driver, win_prob}]
  const sortedPreds = React.useMemo(() => {
    if (!result || !result.predictions) return [];
    return Object.entries(result.predictions)
      .map(([driver, v]) => ({ driver, win_prob: v.win_prob ?? v?.win_prob ?? (v?.win_prob === 0 ? 0 : v) }))
      .sort((a, b) => b.win_prob - a.win_prob);
  }, [result]);

  return (
    <section className="bg-white rounded p-4 shadow">
      <h2 className="text-xl font-semibold mb-2">Prediction Kit (Post-Qualifying)</h2>

      <div className="flex gap-2 items-center mb-3">
        <label className="text-sm">VER pos</label>
        <input
          className="border p-1 w-16"
          type="number"
          min={1}
          value={qualMap.VER}
          onChange={(e) => setQualMap({ ...qualMap, VER: Number(e.target.value) })}
        />
        <label className="text-sm">LEC pos</label>
        <input
          className="border p-1 w-16"
          type="number"
          min={1}
          value={qualMap.LEC}
          onChange={(e) => setQualMap({ ...qualMap, LEC: Number(e.target.value) })}
        />
        <button
          className="ml-4 px-3 py-1 bg-indigo-600 text-white rounded disabled:opacity-50"
          onClick={run}
          disabled={loading}
        >
          {loading ? "Running…" : "Run"}
        </button>
      </div>

      {error && <div className="text-red-600 mb-3">{error}</div>}

      {result && sortedPreds.length > 0 && (
        <div className="mt-3">
          <h3 className="font-medium mb-2">Predicted finishing order</h3>
          <div className="space-y-2">
            {sortedPreds.map((p, idx) => (
              <div key={p.driver} className="flex items-center gap-3">
                <div className="w-8 text-sm font-medium">{idx + 1}.</div>
                <div className="w-16 text-sm font-semibold">{p.driver}</div>
                <div className="flex-1 bg-gray-100 rounded overflow-hidden h-5">
                  <div
                    className="h-5 rounded"
                    style={{
                      width: `${Math.max(3, Math.round((p.win_prob ?? 0) * 100))}%`,
                      background: "#4f46e5",
                    }}
                  />
                </div>
                <div className="w-20 text-right text-sm">{((p.win_prob ?? 0) * 100).toFixed(1)}%</div>
              </div>
            ))}
          </div>

          <pre className="mt-3 bg-gray-50 p-2 rounded text-xs overflow-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </section>
  );
}
