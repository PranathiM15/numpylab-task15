"""NumPy Insight Lab — a lightweight statistics web app using Python's standard library."""
from __future__ import annotations

import json
import math
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import numpy as np

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
MAX_DATA_POINTS = 500
MAX_ABS_VALUE = 1_000_000_000_000

SAMPLES = {
    "student": {
        "name": "Student performance scores",
        "description": "A small score set with one unusually low result.",
        "unit": "marks",
        "values": [72, 85, 91, 68, 88, 94, 76, 83, 79, 97, 42],
    },
    "sales": {
        "name": "Monthly sales values",
        "description": "Monthly sales figures with one unusually high result.",
        "unit": "units sold",
        "values": [120, 135, 128, 142, 138, 155, 149, 162, 157, 171, 410],
    },
}


def _rounded(value: float) -> float:
    """Round floating-point output for readable, stable JSON responses."""
    return round(float(value), 4)


def analyze_values(values: list[float]) -> dict:
    """Calculate descriptive statistics and IQR outliers for at least 3 values."""
    if not isinstance(values, list):
        raise ValueError("Send the observations as a list of numbers.")
    if len(values) < 3:
        raise ValueError("Please enter at least 3 numerical observations.")
    if len(values) > MAX_DATA_POINTS:
        raise ValueError(f"Please enter no more than {MAX_DATA_POINTS} observations.")

    checked: list[float] = []
    for index, value in enumerate(values, start=1):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Observation {index} is not a valid number.")
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"Observation {index} must be a finite number.")
        if abs(number) > MAX_ABS_VALUE:
            raise ValueError(f"Observation {index} is too large. Keep values between ±{MAX_ABS_VALUE:,}.")
        checked.append(number)

    data = np.asarray(checked, dtype=np.float64)
    mean = float(np.mean(data))
    median = float(np.median(data))
    std_dev = float(np.std(data, ddof=0))  # Population standard deviation (NumPy default).
    minimum = float(np.min(data))
    maximum = float(np.max(data))
    q1, q3 = (float(v) for v in np.percentile(data, [25, 75]))
    iqr = q3 - q1
    low_fence = q1 - 1.5 * iqr
    high_fence = q3 + 1.5 * iqr

    observations = []
    outliers = []
    for index, value in enumerate(checked, start=1):
        kind = "low" if value < low_fence else "high" if value > high_fence else None
        observation = {
            "index": index,
            "value": _rounded(value),
            "is_outlier": kind is not None,
            "outlier_kind": kind,
        }
        observations.append(observation)
        if kind is not None:
            outliers.append(observation)

    return {
        "count": len(checked),
        "mean": _rounded(mean),
        "median": _rounded(median),
        "std_dev": _rounded(std_dev),
        "min": _rounded(minimum),
        "max": _rounded(maximum),
        "range": _rounded(maximum - minimum),
        "q1": _rounded(q1),
        "q3": _rounded(q3),
        "iqr": _rounded(iqr),
        "low_fence": _rounded(low_fence),
        "high_fence": _rounded(high_fence),
        "observations": observations,
        "sorted_values": [_rounded(v) for v in sorted(checked)],
        "outliers": outliers,
        "std_dev_type": "population",
        "outlier_rule": "1.5 × IQR",
    }


class InsightHandler(BaseHTTPRequestHandler):
    server_version = "NumPyInsightLab/1.0"

    def log_message(self, fmt: str, *args) -> None:
        # Keep the terminal output useful without logging posted dataset contents.
        print(f"[{self.log_date_time_string()}] {self.address_string()} - {fmt % args}")

    def _send_json(self, payload: dict, status: int = 200) -> None:
        content = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def _send_file(self, path: Path, content_type: str) -> None:
        if not path.is_file():
            self.send_error(404, "File not found")
            return
        content = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler method name
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
        elif path == "/static/style.css":
            self._send_file(STATIC_DIR / "style.css", "text/css; charset=utf-8")
        elif path == "/static/app.js":
            self._send_file(STATIC_DIR / "app.js", "text/javascript; charset=utf-8")
        elif path == "/api/health":
            self._send_json({"status": "ok", "app": "NumPy Insight Lab", "numpy_version": np.__version__})
        elif path == "/api/samples":
            self._send_json({"samples": SAMPLES})
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler method name
        if urlparse(self.path).path != "/api/analyze":
            self._send_json({"error": "Not found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 100_000:
                self._send_json({"error": "Request body is empty or too large."}, 413)
                return
            body = self.rfile.read(length)
            request = json.loads(body.decode("utf-8"))
            if not isinstance(request, dict):
                raise ValueError("Request must be a JSON object.")
            results = analyze_values(request.get("values"))
            results["dataset_name"] = str(request.get("dataset_name", "Custom dataset"))[:100]
            results["unit"] = str(request.get("unit", "observations"))[:40]
            self._send_json(results)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json({"error": "Request body must be valid JSON."}, 400)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, 400)
        except BrokenPipeError:
            return


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0" if "PORT" in os.environ else "127.0.0.1")
    # Hosting services commonly provide PORT; local use defaults to 8000.
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), InsightHandler)
    print("\n  NUMPY INSIGHT LAB")
    print("  ------------------------------------------")
    print(f"  Open in your browser: http://127.0.0.1:{port}")
    print("  Powered by Python + NumPy; no notebook needed.")
    print("  Press Ctrl+C to stop the server.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
