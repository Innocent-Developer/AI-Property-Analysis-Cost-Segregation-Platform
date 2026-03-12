# API Reference – AI Property Analysis & Cost Segregation Platform

Complete guide to all API endpoints, routers, request/response schemas, and usage.

---

## Base URL & Configuration

| Item | Value |
|------|--------|
| **Base URL** | `http://localhost:8000` (development) |
| **API prefix** | `/api` |
| **Full API base** | `http://localhost:8000/api` |
| **OpenAPI (Swagger)** | `http://localhost:8000/docs` |
| **ReDoc** | `http://localhost:8000/redoc` |

All endpoints below are relative to the API prefix unless noted.

---

## Router Overview

| Router | Tag | File | Description |
|--------|-----|------|-------------|
| Health | `health` | `app/routes/health.py` | Liveness and DB connectivity |
| Properties | `properties` | `app/routes/property.py` | Property CRUD |
| Images | `images` | `app/routes/image.py` | Image upload per property |
| Analysis | `analysis` | `app/routes/analysis.py` | Full property analysis pipeline |

Every route is mounted under `/api` and uses the shared **database session** dependency (`get_db`).

---

## 1. Health

### `GET /api/health`

Health check: verifies API and database connectivity.

**Dependencies:** Database session (runs `SELECT 1`).

**Response:** `200 OK`

```json
{
  "status": "ok",
  "app": "AI Property Analysis & Cost Segregation API",
  "environment": "development",
  "version": "0.1.0"
}
```

**Errors:** If the database is unreachable, the request may fail with a 500 (depends on DB dependency).

**Example:**
```bash
curl -X GET "http://localhost:8000/api/health"
```

---

## 2. Properties

### `POST /api/property`

Create a new property.

**Request body:** `PropertyCreate` (JSON)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | UUID | No | User owning the property (nullable) |
| `address` | string | Yes | Property address |
| `property_type` | string | Yes | Type of property (e.g. residential, commercial) |
| `improvement_basis` | number | No | Improvement/cost basis for financial calculations |

**Example request:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "address": "123 Main St, City, State",
  "property_type": "residential",
  "improvement_basis": 250000.50
}
```

**Response:** `201 Created` – `PropertyResponse`

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Auto-generated property ID |
| `user_id` | UUID \| null | As provided or null |
| `address` | string | |
| `property_type` | string | |
| `improvement_basis` | number \| null | |
| `created_at` | datetime \| null | |
| `updated_at` | datetime \| null | |
| `images` | array | List of `ImageResponse` (default `[]`) |
| `assets` | array | List of `AssetResponse` (default `[]`) |
| `reports` | array | List of `ReportResponse` (default `[]`) |

**Example:**
```bash
curl -X POST "http://localhost:8000/api/property" \
  -H "Content-Type: application/json" \
  -d '{"address":"123 Main St","property_type":"residential","improvement_basis":250000}'
```

---

### `GET /api/property/{property_id}`

Get a single property by ID.

**Path parameters:**

| Name | Type | Description |
|------|------|-------------|
| `property_id` | UUID | Property UUID |

**Response:** `200 OK` – `PropertyResponse` (same shape as above, with related `images`, `assets`, `reports` if loaded).

**Errors:**

| Status | Condition |
|--------|-----------|
| `404 Not Found` | No property with the given ID |

**Example:**
```bash
curl -X GET "http://localhost:8000/api/property/550e8400-e29b-41d4-a716-446655440000"
```

---

### `GET /api/properties`

List properties with pagination.

**Query parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `skip` | integer | `0` | Number of records to skip |
| `limit` | integer | `50` | Max number of records to return |

**Response:** `200 OK` – array of `PropertyResponse`

**Example:**
```bash
curl -X GET "http://localhost:8000/api/properties?skip=0&limit=20"
```

---

## 3. Images

### `POST /api/property/{property_id}/images`

Upload one or more images for a property. Images are validated (jpg, jpeg, png, webp), resized, compressed, and stored under `storage/properties/{property_id}/`. Also enqueues the background pipeline (AI detection → report generation) for this property.

**Path parameters:**

| Name | Type | Description |
|------|------|-------------|
| `property_id` | UUID | Property to attach images to |

**Request body:** `multipart/form-data` – field name `files`, one or more image files.

**Accepted formats:** `jpg`, `jpeg`, `png`, `webp`

**Response:** `201 Created` – array of `ImageResponse`

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Image record ID |
| `property_id` | UUID | |
| `image_url` | string | Path like `/storage/properties/{property_id}/{filename}` |
| `uploaded_at` | datetime | |
| `detections` | array | List of `DetectionResponse` (default `[]`) |

**Errors:**

| Status | Condition |
|--------|-----------|
| `404 Not Found` | Property not found |
| `400 Bad Request` | Unsupported format or invalid image data |

**Example:**
```bash
curl -X POST "http://localhost:8000/api/property/550e8400-e29b-41d4-a716-446655440000/images" \
  -F "files=@photo1.jpg" \
  -F "files=@photo2.png"
```

---

## 4. Analysis

### `POST /api/analyze-property/{property_id}`

Run the full property analysis pipeline for the given property: load images → preprocess → AI detection (3 models) → normalize labels → deduplicate → classify assets → financial calculations → generate Excel report → store report → return report URL.

**Path parameters:**

| Name | Type | Description |
|------|------|-------------|
| `property_id` | UUID | Property to analyze |

**Request body:** None.

**Response:** `200 OK`

```json
{
  "report_url": "storage/reports/property_550e8400-e29b-41d4-a716-446655440000_20250311-123456.xlsx"
}
```

`report_url` is the filesystem path under the project root where the Excel file was saved. The same path is stored in the `reports` table for this property.

**Errors:**

| Status | Condition |
|--------|-----------|
| `404 Not Found` | Property not found |
| `400 Bad Request` | No images for property, or no detections produced from images |

**Example:**
```bash
curl -X POST "http://localhost:8000/api/analyze-property/550e8400-e29b-41d4-a716-446655440000"
```

---

## 5. Reports

### `GET /api/report/{report_id}`

Download the Excel report file by report ID. Returns the file with `Content-Disposition: attachment`.

**Path parameters:** `report_id` (integer).

**Response:** `200 OK` — binary Excel file.

**Errors:** `404 Not Found` if report or file does not exist.

**Example:**
```bash
curl -O -J "http://localhost:8000/api/report/1"
```

### `GET /api/property/{property_id}/reports`

List all reports for a property (newest first). Use a returned `id` with `GET /api/report/{report_id}` to download.

**Path parameters:** `property_id` (UUID).

**Response:** `200 OK` — array of `ReportResponse` (`id`, `property_id`, `report_url`, `created_at`).

---

## Response Schemas Reference

### PropertyResponse
- `id` (UUID), `user_id` (UUID | null), `address`, `property_type`, `improvement_basis` (number | null)
- `created_at`, `updated_at` (datetime | null)
- `images` (array of ImageResponse), `assets` (array of AssetResponse), `reports` (array of ReportResponse)

### PropertyCreate (request only)
- `user_id` (UUID | null, optional), `address`, `property_type`, `improvement_basis` (number | null, optional)

### ImageResponse
- `id`, `property_id`, `image_url`, `uploaded_at`, `detections` (array of DetectionResponse)

### DetectionResponse
- `id`, `image_id`, `label`, `confidence`, `normalized_label` (string | null)

### AssetResponse
- `id`, `property_id`, `asset_name`, `quantity`, `asset_life`

### ReportResponse
- `id`, `property_id`, `report_url`, `created_at`

---

## Summary Table

| Method | Endpoint | Tag | Description |
|--------|----------|-----|-------------|
| GET | `/api/health` | health | Health + DB check |
| POST | `/api/property` | properties | Create property |
| GET | `/api/property/{property_id}` | properties | Get property by ID |
| GET | `/api/properties` | properties | List properties (paginated) |
| POST | `/api/property/{property_id}/images` | images | Upload images for property |
| POST | `/api/analyze-property/{property_id}` | analysis | Run full analysis, return report URL |
| GET | `/api/report/{report_id}` | reports | Download report Excel file by ID |
| GET | `/api/property/{property_id}/reports` | reports | List reports for property (newest first) |

---

## Report download

- **GET /api/report/{report_id}** — Returns the Excel file for the given report ID (`Content-Disposition` attachment).
- **GET /api/property/{property_id}/reports** — Returns list of `ReportResponse` for that property; use `report_id` with the download endpoint to get the file.

---

## Notes

- **Rate limiting:** Default `200/minute` per client (configurable via `RATE_LIMIT_DEFAULT`). Uses SlowAPI when installed.
- **Authentication:** Optional API key auth: set `AUTH_ENABLED=true` and `API_KEY=your-secret` in `.env`; then use `X-API-Key` header. Use `Depends(optional_api_key)` from `app.auth.dependencies` on routes to protect them.
- **Background pipeline:** Uploading images triggers a Celery chain (image_processing → ai_detection → report_generation). Reports may appear asynchronously; the synchronous way to get a report immediately is `POST /api/analyze-property/{property_id}`.
