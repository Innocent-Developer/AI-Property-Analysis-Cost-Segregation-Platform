#!/usr/bin/env bash
# Quick API smoke test (run with API on http://127.0.0.1:8000)
set -e
BASE="${1:-http://127.0.0.1:8000}"

echo "=== 1. GET /api/health ==="
curl -sf "$BASE/api/health" | python3 -m json.tool

echo ""
echo "=== 2. POST /api/property ==="
PROP=$(curl -sf -X POST "$BASE/api/property" -H "Content-Type: application/json" \
  -d '{"address":"456 Smoke Test Ave","property_type":"residential","improvement_basis":200000}')
echo "$PROP" | python3 -m json.tool
PID=$(echo "$PROP" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo ""
echo "=== 3. GET /api/properties ==="
curl -sf "$BASE/api/properties" | python3 -m json.tool | head -25

echo ""
echo "=== 4. GET /api/property/$PID ==="
curl -sf "$BASE/api/property/$PID" | python3 -m json.tool | head -20

echo ""
echo "=== 5. POST /api/property/$PID/images (valid PNG) ==="
# Create minimal valid PNG
python3 -c "
from PIL import Image
img = Image.new('RGB', (20, 20), color='blue')
img.save('/tmp/smoke_test.png')
"
curl -sf -X POST "$BASE/api/property/$PID/images" -F "files=@/tmp/smoke_test.png" --max-time 10 | python3 -m json.tool

echo ""
echo "=== 6. POST /api/analyze-property/$PID (200=report_url, 400=no images/detections) ==="
ANALYZE=$(curl -s -X POST "$BASE/api/analyze-property/$PID" --max-time 60 -w "\nHTTP:%{http_code}")
echo "$ANALYZE" | head -1 | python3 -m json.tool 2>/dev/null || echo "$ANALYZE" | head -1

echo ""
echo "=== 7. GET /api/property/$PID/reports ==="
curl -sf "$BASE/api/property/$PID/reports" | python3 -m json.tool

echo ""
echo "=== All smoke tests passed ==="
