# backend/app/api/telemetry.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json
import os
import traceback

router = APIRouter()
HERE = os.path.dirname(__file__)
DATA_PATH = os.path.join(HERE, "..", "data", "sample_telemetry.json")
FASTF1_CACHE = os.path.join(HERE, "..", "data", "fastf1_cache")

# helper: safe read sample JSON (handles BOM)
def _read_sample(driver_id):
    try:
        with open(DATA_PATH, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        return data.get(driver_id, data.get("VER"))
    except Exception:
        return {"error": "sample telemetry unavailable"}

# attempt to import fastf1 (optional)
try:
    import fastf1  # type: ignore
    FASTF1_AVAILABLE = True
    try:
        fastf1.Cache.enable_cache(FASTF1_CACHE)
    except Exception:
        # ignore cache-enable errors; still try to use fastf1
        pass
except Exception:
    FASTF1_AVAILABLE = False

# Static race list (2023 sample) - frontend will show these immediately
STATIC_RACES_2023 = [
    {"id": "2023-01-bahrain", "name": "Bahrain GP 2023"},
    {"id": "2023-02-jeddah", "name": "Saudi Arabia GP 2023"},
    {"id": "2023-03-auc", "name": "Australia GP 2023"},
    {"id": "2023-04-miami", "name": "Miami GP 2023"},
    {"id": "2023-05-italy", "name": "Monaco GP 2023"},
    {"id": "2023-06-spanish", "name": "Spain GP 2023"},
    {"id": "2023-07-austria", "name": "Austria GP 2023"},
    {"id": "2023-08-belgium", "name": "Belgium GP 2023"},
    {"id": "2023-09-netherlands", "name": "Netherlands GP 2023"},
    {"id": "2023-10-sanmarino", "name": "San Marino GP 2023"},
    {"id": "2023-11-singapore", "name": "Singapore GP 2023"},
    {"id": "2023-12-japan", "name": "Japan GP 2023"},
    {"id": "2023-13-austin", "name": "United States GP 2023"},
    {"id": "2023-14-mexico", "name": "Mexico GP 2023"},
    {"id": "2023-15-sao_paulo", "name": "Brazil GP 2023"},
    {"id": "2023-16-las_vegas", "name": "Las Vegas GP 2023"},
    {"id": "2023-17-abudhabi", "name": "Abu Dhabi GP 2023"}
]

@router.get("/races")
def list_races():
    """
    Return available races. We return a static 2023 list by default.
    If you want dynamic calendar from FastF1, I can implement that (requires fastf1 + network).
    """
    return STATIC_RACES_2023

@router.get("/race/{race_id}/drivers")
def drivers_for_race(race_id: str):
    """
    Return list of drivers for a given race_id.
    Tries FastF1 to extract drivers from session data, falls back to a small static list.
    """
    # fallback static stub
    fallback = [
        {"driverId": "VER", "name": "Max Verstappen"},
        {"driverId": "LEC", "name": "Charles Leclerc"},
        {"driverId": "HAM", "name": "Lewis Hamilton"},
        {"driverId": "ALO", "name": "Fernando Alonso"},
    ]

    if FASTF1_AVAILABLE:
        try:
            parts = race_id.split("-")
            year = int(parts[0]) if parts and parts[0].isdigit() else None
            gp_slug = parts[-1] if len(parts) >= 2 else None

            session = None
            # try common session types
            for sname in ("R", "S", "Q", "FP3"):
                try:
                    session = fastf1.get_session(year, gp_slug, sname)
                    session.load()
                    break
                except Exception:
                    session = None

            if session is not None and hasattr(session, "laps"):
                laps_df = session.laps
                # FastF1's laps may contain a 'Driver' column with abbreviations
                if "Driver" in laps_df.columns:
                    drivers = sorted(list(map(str, laps_df["Driver"].unique())))
                    return [{"driverId": d, "name": d} for d in drivers]
                # fallback to session.results if available
                if hasattr(session, "results") and session.results is not None:
                    try:
                        res = session.results
                        if "Abbreviation" in res.columns:
                            drivers = sorted(list(map(str, res["Abbreviation"].unique())))
                            return [{"driverId": d, "name": d} for d in drivers]
                    except Exception:
                        pass
        except Exception as e:
            print("FastF1 drivers_for_race error:", e)
            print(traceback.format_exc())

    return fallback

@router.get("/race/{race_id}/telemetry/{driver_id}")
def telemetry_for_driver(race_id: str, driver_id: str):
    """
    Return telemetry for a driver in a race.
    Tries FastF1 (Race -> Sprint -> Qualy -> FP3), falls back to sample JSON.
    """
    # FastF1 path
    if FASTF1_AVAILABLE:
        try:
            parts = race_id.split("-")
            year = int(parts[0]) if parts and parts[0].isdigit() else None
            gp_slug = parts[-1] if len(parts) >= 2 else None

            session = None
            for sname in ("R", "S", "Q", "FP3"):
                try:
                    session = fastf1.get_session(year, gp_slug, sname)
                    session.load()
                    break
                except Exception:
                    session = None

            if session is None:
                return JSONResponse(content=_read_sample(driver_id))

            # try picking laps by driver code
            try:
                laps = session.laps.pick_driver(driver_id)
            except Exception:
                # sometimes driver_id might be driver number; attempt pick by driver number if numeric
                try:
                    laps = session.laps.pick_driver(int(driver_id))
                except Exception:
                    laps = session.laps.loc[session.laps["Driver"] == driver_id]

            if laps is None or getattr(laps, "empty", False):
                return JSONResponse(content=_read_sample(driver_id))

            out = {"laps": [], "tyres": []}
            # iterate laps safely (use iterlaps() if available)
            try:
                iter_laps = laps.iterlaps()
            except Exception:
                # fallback to iterrows if necessary
                iter_laps = ((idx, row) for idx, row in laps.iterrows())

            # limit to first 100 laps to avoid big payloads
            count = 0
            for lap_tuple in iter_laps:
                # lap_tuple can be (index, row) for iterrows or object for iterlaps
                row = None
                if isinstance(lap_tuple, tuple) and len(lap_tuple) == 2:
                    row = lap_tuple[1]
                else:
                    # iterlaps row-like returned directly
                    row = lap_tuple

                # robust extraction
                try:
                    lapnum = int(row.get("LapNumber", row.get("lapNumber", 0)))
                except Exception:
                    lapnum = int(row.get("LapNumber", 0) or 0)

                laptime = None
                if row.get("LapTime") is not None:
                    try:
                        laptime = round(row["LapTime"].total_seconds(), 3)
                    except Exception:
                        laptime = None

                sectors = []
                for s_key in ("Sector1Time", "Sector2Time", "Sector3Time"):
                    if s_key in row and row[s_key] is not None:
                        try:
                            sectors.append(round(row[s_key].total_seconds(), 3))
                        except Exception:
                            pass

                avg_speed = None
                if "Speed" in row and row["Speed"] is not None:
                    try:
                        avg_speed = float(row["Speed"])
                    except Exception:
                        avg_speed = None

                out["laps"].append({"lap": lapnum, "time": laptime, "speed": avg_speed, "sector": sectors})

                # tyre compound detection
                compound = None
                if "Compound" in row and row["Compound"] is not None:
                    compound = row["Compound"]
                elif "TyreCompound" in row and row["TyreCompound"] is not None:
                    compound = row["TyreCompound"]
                if compound:
                    out["tyres"].append(str(compound))

                count += 1
                if count >= 100:
                    break

            if not out["tyres"]:
                out["tyres"] = ["unknown"]

            return JSONResponse(content=out)

        except Exception as e:
            print("FastF1 telemetry error:", e)
            print(traceback.format_exc())
            return JSONResponse(content=_read_sample(driver_id))

    # FastF1 not available, fallback to sample JSON
    return JSONResponse(content=_read_sample(driver_id))
