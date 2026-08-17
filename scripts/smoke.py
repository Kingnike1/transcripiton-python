"""Small operational smoke test for a running AMIP instance."""

import json
import sys
import urllib.request

base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8000"

with urllib.request.urlopen(f"{base_url}/health", timeout=5) as response:
    health = json.load(response)
    assert response.status == 200
    assert health["status"] == "healthy"

with urllib.request.urlopen(f"{base_url}/meetings", timeout=5) as response:
    body = response.read().decode("utf-8")
    assert response.status == 200
    assert "Reuniões" in body

print(f"AMIP smoke test OK: {base_url}")
