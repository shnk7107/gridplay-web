import axios from "axios";
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api";

export const fetchRaces = () => axios.get(`${API_BASE}/telemetry/races`).then(r=>r.data);
export const fetchDrivers = (raceId) => axios.get(`${API_BASE}/telemetry/race/${raceId}/drivers`).then(r=>r.data);
export const fetchTelemetry = (raceId, driverId) => axios.get(`${API_BASE}/telemetry/race/${raceId}/telemetry/${driverId}`).then(r=>r.data);
export const postPredict = (payload) => axios.post(`${API_BASE}/predict/post_qualifying`, payload).then(r=>r.data);
export const submitBattle = (payload) => axios.post(`${API_BASE}/battles/submit`, payload).then(r=>r.data);
