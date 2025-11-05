import React, { useState } from "react";
import { submitBattle } from "../api";

export default function FanBattle() {
  const [userId, setUserId] = useState("guest123");
  const [pred, setPred] = useState({ VER: 1, LEC: 2 });
  const [res, setRes] = useState(null);

  const submit = async () => {
    try {
      const r = await submitBattle({ user_id: userId, race_id: "2023-01-bahrain", prediction: pred });
      setRes(r);
    } catch (err) {
      console.error("Battle submit error:", err);
      alert("Failed to submit battle. See console for details.");
    }
  };

  return (
    <section className="bg-white rounded p-4 shadow">
      <h2 className="text-xl font-semibold mb-2">Fan vs AI Battles</h2>
      <div className="flex gap-2 items-center mb-3">
        <input className="border p-1" value={userId} onChange={(e) => setUserId(e.target.value)} />
        <label>VER</label>
        <input
          className="border p-1 w-16"
          type="number"
          value={pred.VER}
          onChange={(e) => setPred({ ...pred, VER: Number(e.target.value) })}
        />
        <label>LEC</label>
        <input
          className="border p-1 w-16"
          type="number"
          value={pred.LEC}
          onChange={(e) => setPred({ ...pred, LEC: Number(e.target.value) })}
        />
        <button onClick={submit} className="px-3 py-1 bg-yellow-600 rounded">
          Submit
        </button>
      </div>

      {res && <pre className="bg-gray-100 p-2 rounded">{JSON.stringify(res, null, 2)}</pre>}
    </section>
  );
}
