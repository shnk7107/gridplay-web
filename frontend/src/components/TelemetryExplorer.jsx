import React, { useEffect, useState } from "react";
import { fetchRaces, fetchDrivers, fetchTelemetry } from "../api";
import * as d3 from "d3";

export default function TelemetryExplorer(){
  const [races, setRaces] = useState([]);
  const [race, setRace] = useState(null);
  const [drivers, setDrivers] = useState([]);
  const [driver, setDriver] = useState("VER");
  const [telemetry, setTelemetry] = useState(null);

  useEffect(()=>{ fetchRaces().then(setRaces).catch(()=>setRaces([])) }, []);
  useEffect(()=>{ if(race) fetchDrivers(race).then(setDrivers) }, [race]);
  useEffect(()=>{ if(race && driver) fetchTelemetry(race, driver).then(setTelemetry) }, [race, driver]);

  useEffect(()=>{
    if(!telemetry) return;
    const data = telemetry.laps.map(l => ({lap: l.lap, time: l.time}));
    d3.select("#telemetry-chart").selectAll("*").remove();
    const width = 700, height=200, margin = {l:30,r:10,t:10,b:30};
    const svg = d3.select("#telemetry-chart").append("svg").attr("width", width).attr("height", height);
    const x = d3.scaleLinear().domain(d3.extent(data, d=>d.lap)).range([margin.l, width-margin.r]);
    const y = d3.scaleLinear().domain([d3.min(data,d=>d.time)*0.99, d3.max(data,d=>d.time)*1.01]).range([height-margin.b, margin.t]);
    const line = d3.line().x(d=>x(d.lap)).y(d=>y(d.time));
    svg.append("path").datum(data).attr("d", line).attr("fill","none").attr("stroke","steelblue");
    svg.append("g").attr("transform",`translate(0,${height-margin.b})`).call(d3.axisBottom(x).ticks(data.length));
    svg.append("g").attr("transform",`translate(${margin.l},0)`).call(d3.axisLeft(y));
  }, [telemetry]);

  return (
    <section className="bg-white rounded p-4 shadow">
      <h2 className="text-xl font-semibold mb-2">Telemetry Explorer</h2>
      <div className="flex gap-4 mb-3">
        <select onChange={e=>setRace(e.target.value)} value={race || ""} className="border p-2">
          <option value="">Select race</option>
          {races.map(r=> <option key={r.id} value={r.id}>{r.name}</option>)}
        </select>
        <select onChange={e=>setDriver(e.target.value)} value={driver} className="border p-2">
          {drivers.map(d => <option key={d.driverId} value={d.driverId}>{d.name}</option>)}
        </select>
      </div>

      <div id="telemetry-chart" />
      {telemetry && (
        <div className="mt-3 text-sm text-gray-700">
          <strong>Tyres:</strong> {telemetry.tyres.join(", ")}
        </div>
      )}
    </section>
  );
}
