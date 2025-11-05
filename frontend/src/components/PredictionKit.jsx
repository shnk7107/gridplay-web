import React, {useState} from "react";
import { postPredict } from "../api";

export default function PredictionKit(){
  const [qualMap, setQualMap] = useState({VER:1, LEC:2});
  const [result, setResult] = useState(null);

  const run = async () => {
    const payload = { race_id: "2023-01-bahrain", qualifying_pos: qualMap };
    const res = await postPredict(payload);
    setResult(res);
  }

  return (
    <section className="bg-white rounded p-4 shadow">
      <h2 className="text-xl font-semibold mb-2">Prediction Kit (Post-Qualifying)</h2>
      <div className="flex gap-2 items-center mb-3">
        <label className="text-sm">VER pos</label>
        <input className="border p-1 w-16" type="number" value={qualMap.VER} onChange={e=>setQualMap({...qualMap, VER: Number(e.target.value)})} />
        <label className="text-sm">LEC pos</label>
        <input className="border p-1 w-16" type="number" value={qualMap.LEC} onChange={e=>setQualMap({...qualMap, LEC: Number(e.target.value)})} />
        <button className="ml-4 px-3 py-1 bg-indigo-600 text-white rounded" onClick={run}>Run</button>
      </div>

      {result && (
        <div className="text-sm">
          <pre className="bg-gray-100 p-2 rounded overflow-auto">{JSON.stringify(result.predictions, null, 2)}</pre>
        </div>
      )}
    </section>
  );
}
