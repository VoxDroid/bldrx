import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def _default_telemetry_file() -> Path:
    if os.name == "nt":
        appdata = os.getenv("APPDATA") or Path.home()
        return Path(appdata) / "bldrx" / "telemetry.log"
    return Path.home() / ".bldrx" / "telemetry.log"


class Telemetry:
    """Simple opt-in telemetry helper.

    Behavior:
    - Disabled by default. Opt-in by setting BLDRX_ENABLE_TELEMETRY=1 or via CLI helper.
    - Writes newline-delimited JSON events to a local telemetry log file by default.
    - If BLDRX_TELEMETRY_ENDPOINT is set, attempts to POST JSON events to that endpoint (best-effort; failures are ignored).
    """

    def __init__(self, enabled: Optional[bool] = None, logfile: Optional[Path] = None):
        env = os.getenv("BLDRX_ENABLE_TELEMETRY")
        if enabled is None:
            self.enabled = env == "1"
        else:
            self.enabled = bool(enabled)
        self.logfile = Path(logfile) if logfile else _default_telemetry_file()
        # allow endpoint override (if provided, do best-effort POST)
        self.endpoint = os.getenv("BLDRX_TELEMETRY_ENDPOINT")

    def enable(self):
        os.environ["BLDRX_ENABLE_TELEMETRY"] = "1"
        self.enabled = True
        return True

    def disable(self):
        os.environ.pop("BLDRX_ENABLE_TELEMETRY", None)
        self.enabled = False
        return True

    def status(self):
        return {
            "enabled": self.enabled,
            "endpoint": self.endpoint,
            "logfile": str(self.logfile),
        }

    def track_event(self, event: str, payload: Optional[dict] = None) -> bool:
        if not self.enabled:
            return False
        payload = payload or {}
        record = {
            "event": event,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        try:
            self.logfile.parent.mkdir(parents=True, exist_ok=True)
            with self.logfile.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, separators=(",", ":")) + "\n")
        except Exception:
            # best-effort: never raise from telemetry
            return False
        # optionally send to endpoint (best-effort)
        if self.endpoint:
            try:
                import urllib.request

                req = urllib.request.Request(
                    self.endpoint,
                    data=json.dumps(record).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=5):
                    pass
            except Exception:
                # ignore network failures
                pass
        return True


# module-level convenience instance
_default = Telemetry()


def enable():
    return _default.enable()


def disable():
    return _default.disable()


def status():
    return _default.status()


def track_event(event, payload=None):
    return _default.track_event(event, payload)
