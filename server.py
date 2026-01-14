#!/usr/bin/env python3
"""
Starlink Dashboard Server - FastAPI backend for Starlink telemetry.

A real-time web dashboard for monitoring Starlink dish statistics
via the local gRPC API.

Requires: starlink-grpc-tools (https://github.com/sparky8512/starlink-grpc-tools)
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Find starlink-grpc-tools - check environment variable, common locations, or PATH
TOOLS_DIR = os.environ.get("STARLINK_GRPC_TOOLS")
if TOOLS_DIR:
    sys.path.insert(0, TOOLS_DIR)
else:
    # Try common installation locations
    common_paths = [
        Path.home() / "starlink-grpc-tools",
        Path.home() / "src" / "starlink-grpc-tools",
        Path("/opt/starlink-grpc-tools"),
        Path("/usr/local/lib/starlink-grpc-tools"),
    ]
    for path in common_paths:
        if path.exists() and (path / "starlink_grpc.py").exists():
            sys.path.insert(0, str(path))
            TOOLS_DIR = str(path)
            break

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

try:
    import starlink_grpc
except ImportError:
    print("Error: starlink_grpc module not found.")
    print("\nInstall starlink-grpc-tools:")
    print("  git clone https://github.com/sparky8512/starlink-grpc-tools.git")
    print("  pip install grpcio yagrc")
    print("\nThen either:")
    print("  - Set STARLINK_GRPC_TOOLS=/path/to/starlink-grpc-tools")
    print("  - Or clone to ~/starlink-grpc-tools")
    sys.exit(1)

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="Starlink Dashboard API",
    description="Real-time Starlink dish telemetry",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Serve the dashboard."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/status")
async def get_status():
    """Get current dish status."""
    try:
        result = starlink_grpc.status_data()
        status = result[0] if len(result) > 0 else {}
        obstruction = result[1] if len(result) > 1 else {}
        alerts = result[2] if len(result) > 2 else {}

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "obstruction": obstruction,
            "alerts": alerts,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@app.get("/api/history")
async def get_history():
    """Get historical data for charts."""
    try:
        bulk = starlink_grpc.history_bulk_data(-1)
        general = bulk[0] if len(bulk) > 0 else {}
        data = bulk[1] if len(bulk) > 1 else {}

        # Calculate stats
        stats = {
            "samples": general.get("samples", 0),
            "end_counter": general.get("end_counter", 0),
        }

        # Power stats
        if "power_w" in data:
            power_arr = [p for p in data["power_w"] if p is not None]
            if power_arr:
                stats["power"] = {
                    "current": power_arr[-1],
                    "mean": sum(power_arr) / len(power_arr),
                    "min": min(power_arr),
                    "max": max(power_arr),
                }

        # Latency stats
        if "pop_ping_latency_ms" in data:
            lat_arr = [l for l in data["pop_ping_latency_ms"] if l is not None]
            if lat_arr:
                stats["latency"] = {
                    "current": lat_arr[-1],
                    "mean": sum(lat_arr) / len(lat_arr),
                    "min": min(lat_arr),
                    "max": max(lat_arr),
                }

        # Throughput stats
        if "downlink_throughput_bps" in data:
            down = [d for d in data["downlink_throughput_bps"] if d is not None]
            if down:
                stats["download"] = {
                    "current": down[-1],
                    "mean": sum(down) / len(down),
                    "max": max(down),
                }

        if "uplink_throughput_bps" in data:
            up = [u for u in data["uplink_throughput_bps"] if u is not None]
            if up:
                stats["upload"] = {
                    "current": up[-1],
                    "mean": sum(up) / len(up),
                    "max": max(up),
                }

        # Drop rate
        if "pop_ping_drop_rate" in data:
            drops = [d for d in data["pop_ping_drop_rate"] if d is not None]
            if drops:
                stats["drop_rate"] = {
                    "current": drops[-1],
                    "mean": sum(drops) / len(drops),
                }

        # Recent arrays for sparklines (last 60 samples = 1 minute)
        stats["recent"] = {
            "latency": [l for l in (data.get("pop_ping_latency_ms") or [])[-60:] if l is not None],
            "download": [d / 1_000_000 for d in (data.get("downlink_throughput_bps") or [])[-60:] if d is not None],
            "upload": [u / 1_000_000 for u in (data.get("uplink_throughput_bps") or [])[-60:] if u is not None],
            "power": [p for p in (data.get("power_w") or [])[-60:] if p is not None],
        }

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@app.get("/api/location")
async def get_location():
    """Get dish location (if enabled)."""
    try:
        loc = starlink_grpc.location_data()
        return {
            "success": True,
            "location": loc,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@app.post("/api/reboot")
async def reboot_dish():
    """Reboot the dish (use with caution!)."""
    try:
        starlink_grpc.reboot()
        return {"success": True, "message": "Reboot command sent"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/stow")
async def stow_dish(stow: bool = True):
    """Stow or unstow the dish."""
    try:
        starlink_grpc.set_stow_state(stow)
        return {"success": True, "stowed": stow}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def main():
    """Run the server."""
    import argparse
    parser = argparse.ArgumentParser(description="Starlink Dashboard Server")
    parser.add_argument("-p", "--port", type=int, default=8100, help="Port to listen on")
    parser.add_argument("-H", "--host", type=str, default="0.0.0.0", help="Host to bind to")
    args = parser.parse_args()

    print(f"Starting Starlink Dashboard on http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
