"use client";

import { useState } from "react";

export default function HomePage() {
  const [champions, setChampions] = useState("");
  const [lanes, setLanes] = useState("");
  const [runes, setRunes] = useState("");
  const [patch, setPatch] = useState("14.10");
  const [blueSide, setBlueSide] = useState(true);
  const [result, setResult] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      champions: champions
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      lanes: lanes
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      runes: Object.fromEntries(
        runes
          .split(",")
          .map((kv) => kv.split(":"))
          .filter((kv) => kv.length === 2)
          .map(([k, v]) => [k.trim(), v.trim()])
      ),
      patch,
      blue_side: blueSide,
    };

    const base =
      process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";
    const res = await fetch(`${base}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    setResult(
      `${Math.round(data.win_probability * 100)}% (model ${data.model_version})`
    );
  };

  return (
    <main style={{ maxWidth: 720, margin: "2rem auto", padding: 16 }}>
      <h1>DraftDiff</h1>
      <p>Estimate win probability from draft context.</p>
      <form onSubmit={submit} style={{ display: "grid", gap: 12 }}>
        <label>
          Champions (comma-separated)
          <input
            value={champions}
            onChange={(e) => setChampions(e.target.value)}
            placeholder="Ahri, Lee Sin, ..."
          />
        </label>
        <label>
          Lanes (comma-separated)
          <input
            value={lanes}
            onChange={(e) => setLanes(e.target.value)}
            placeholder="mid, jungle, ..."
          />
        </label>
        <label>
          Runes (k:v comma-separated)
          <input
            value={runes}
            onChange={(e) => setRunes(e.target.value)}
            placeholder="keystone:electrocute, secondary:domination"
          />
        </label>
        <label>
          Patch
          <input value={patch} onChange={(e) => setPatch(e.target.value)} />
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <input
            type="checkbox"
            checked={blueSide}
            onChange={(e) => setBlueSide(e.target.checked)}
          />
          Blue side
        </label>
        <button type="submit">Predict</button>
      </form>
      {result && <p style={{ marginTop: 16 }}>Win probability: {result}</p>}
    </main>
  );
}
