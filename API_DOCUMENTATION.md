# API Documentation

## AI Security Risk Detection API

### Base URL
```
http://127.0.0.1:5000
```

---

## Endpoints

### 1. Health Check Endpoint

#### Request
```
GET /health
```

#### Response (200 OK)
```json
{
  "message": "AI Security Risk API is running",
  "status": "healthy",
  "timestamp": "2026-02-15T21:50:00.000000",
  "model_loaded": true,
  "version": "1.0.0"
}
```

---

### 2. Risk Prediction Endpoint

#### Request
```
POST /predict
Content-Type: application/json
```

#### Request Body Schema
```json
{
  "failed_login_attempts": number,        // Required: 0-10
  "login_time_deviation": number,          // Required: 0-1
  "ip_change": integer,                    // Required: 0 or 1
  "device_change": integer,                // Required: 0 or 1
  "transaction_amount_deviation": number   // Required: 0-1
}
```

#### Example Request
```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "failed_login_attempts": 3,
    "login_time_deviation": 0.5,
    "ip_change": 1,
    "device_change": 0,
    "transaction_amount_deviation": 0.8
  }'
```

#### Success Response (200 OK)
```json
{
  "risk_label": 0,
  "risk_score": 45.23,
  "status": "Safe"
}
```

#### Error Response (400 Bad Request)
```json
{
  "error": "Missing required field: ip_change"
}
```

---

## HTTP Status Codes

| Code | Meaning | Scenario |
|------|---------|----------|
| 200 | OK | Success - prediction made or health check passed |
| 400 | Bad Request | Invalid input (missing fields, wrong types, invalid JSON) |
| 404 | Not Found | Endpoint does not exist |
| 405 | Method Not Allowed | Wrong HTTP method for endpoint |
| 500 | Internal Server Error | Server-side error (model not loaded, etc.) |

---

## Error Codes & Messages

### Input Validation Errors (400)

| Error Message | Cause | Solution |
|---------------|-------|----------|
| Request body is missing | No JSON data sent | Include JSON body in request |
| Invalid JSON format in request body | Malformed JSON | Check JSON syntax |
| Missing required field: {field} | A required field is absent | Add the missing field |
| Field 'X' must be numeric | Field has non-numeric value | Use numeric values only |
| Request data is empty | Empty JSON object `{}` | Provide data with all fields |

### Server Errors (500)

| Error Message | Cause | Solution |
|---------------|-------|----------|
| Internal server error | Model not loaded or unexpected error | Check server logs, restart API |

---

## Field Descriptions

### failed_login_attempts
- **Type:** Float
- **Range:** 0-10
- **Description:** Number of failed login attempts in recent history
- **Example:** `3` (3 failed attempts), `0` (no failed attempts)

### login_time_deviation
- **Type:** Float
- **Range:** 0-1 (normalized)
- **Description:** How unusual the login time is compared to user's normal pattern
- **Example:** `0.1` (normal time), `0.9` (very unusual time)

### ip_change
- **Type:** Integer (0 or 1)
- **Range:** Binary
- **Description:** Whether the IP address changed from the last login
- **Example:** `0` (same IP), `1` (different IP)

### device_change
- **Type:** Integer (0 or 1)
- **Range:** Binary
- **Description:** Whether the device changed from the last login
- **Example:** `0` (same device), `1` (different device)

### transaction_amount_deviation
- **Type:** Float
- **Range:** 0-1 (normalized)
- **Description:** How unusual the transaction amount is compared to user's normal patterns
- **Example:** `0.2` (normal amount), `0.95` (very unusual amount)

---

## Response Field Descriptions

### risk_label
- **Type:** Integer
- **Values:** 0 or 1
- **Meaning:** 
  - `0` = Safe transaction
  - `1` = High risk transaction

### risk_score
- **Type:** Float
- **Range:** 0-100 (percentage)
- **Meaning:** Confidence level of the prediction
- **Example:** `45.23%` confidence

### status
- **Type:** String
- **Values:** "Safe" or "High Risk"
- **Meaning:** Human-readable risk classification

---

## Example Scenarios

### Scenario 1: Safe Transaction
```json
REQUEST:
{
  "failed_login_attempts": 0,
  "login_time_deviation": 0.1,
  "ip_change": 0,
  "device_change": 0,
  "transaction_amount_deviation": 0.15
}

RESPONSE (200 OK):
{
  "risk_label": 0,
  "risk_score": 15.42,
  "status": "Safe"
}
```

### Scenario 2: High Risk Transaction
```json
REQUEST:
{
  "failed_login_attempts": 5,
  "login_time_deviation": 0.95,
  "ip_change": 1,
  "device_change": 1,
  "transaction_amount_deviation": 0.92
}

RESPONSE (200 OK):
{
  "risk_label": 1,
  "risk_score": 89.67,
  "status": "High Risk"
}
```

### Scenario 3: Missing Field Error
```json
REQUEST:
{
  "failed_login_attempts": 3,
  "login_time_deviation": 0.5,
  "ip_change": 1,
  "device_change": 0
}
(Missing: transaction_amount_deviation)

RESPONSE (400 Bad Request):
{
  "error": "Missing required field: transaction_amount_deviation"
}
```

### Scenario 4: Invalid Type Error
```json
REQUEST:
{
  "failed_login_attempts": "three",
  "login_time_deviation": 0.5,
  "ip_change": 1,
  "device_change": 0,
  "transaction_amount_deviation": 0.8
}

RESPONSE (400 Bad Request):
{
  "error": "Field 'failed_login_attempts' must be numeric (received: str)"
}
```

---

## Rate Limiting (Future Enhancement)

Currently not implemented. To add:
- Implement Flask-Limiter
- Set rate limits per IP/user
- Return 429 (Too Many Requests) when exceeded

---

## Authentication (Future Enhancement)

Currently not implemented. To add:
- API key validation
- JWT token support
- OAuth 2.0 integration

---

## Version History

### v1.0.0 (2026-02-15)
- Initial release
- Health check endpoint
- Risk prediction endpoint
- Input validation
- Error handling

---

## Support

For issues or questions:
1. Check the README.md
2. Review error messages
3. Check server logs
4. Create a GitHub issue
