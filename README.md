# AI Security Risk Detection API

A production-ready Flask-based Machine Learning API that predicts security risks based on user authentication and transaction behavior patterns.

## 📋 Overview

This API uses a trained Machine Learning model to analyze security features and classify transactions as either **Safe** or **High Risk**. It provides real-time risk assessment with confidence scores for security-critical applications.

## ✨ Features

✅ **RESTful API** - Clean, standards-compliant endpoints  
✅ **ML-Powered** - Scikit-learn trained classification model  
✅ **Production-Ready** - Error handling, logging, validation  
✅ **Input Validation** - Comprehensive request validation  
✅ **Health Checks** - Endpoint monitoring and status reporting  
✅ **JSON Responses** - Structured error and success responses  
✅ **Scalable** - Thread-safe Flask application  

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-security-risk-system.git
   cd ai-security-risk-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   
   **Windows (PowerShell):**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   **Windows (CMD):**
   ```cmd
   venv\Scripts\activate.bat
   ```
   
   **Linux/macOS:**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the API**
   ```bash
   python api/app.py
   ```

   The API will start at: `http://127.0.0.1:5000`

---

## 📡 API Endpoints

### 1. Health Check

**GET** `/` or `/health`

Check if the API is running and operational.

**Response (200 OK):**
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

### 2. Predict Risk

**POST** `/predict`

Analyze security features and predict risk classification.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "failed_login_attempts": 3,
  "login_time_deviation": 0.5,
  "ip_change": 1,
  "device_change": 0,
  "transaction_amount_deviation": 0.8
}
```

**Request Fields:**

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `failed_login_attempts` | float | Number of failed authentication attempts | ✅ Yes |
| `login_time_deviation` | float | Deviation from normal login time (0-1) | ✅ Yes |
| `ip_change` | int | 1 if IP changed from last login, 0 if same | ✅ Yes |
| `device_change` | int | 1 if device changed from last login, 0 if same | ✅ Yes |
| `transaction_amount_deviation` | float | Deviation in transaction amount (0-1) | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "risk_label": 0,
  "risk_score": 45.23,
  "status": "Safe"
}
```

**Response Fields:**

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `risk_label` | int | 0 or 1 | 0 = Safe, 1 = High Risk |
| `risk_score` | float | 0-100 | Confidence percentage |
| `status` | string | "Safe" or "High Risk" | Risk classification |

---

## ❌ Error Responses

### **400 Bad Request** - Invalid input

**Missing body:**
```json
{
  "error": "Request body is missing"
}
```

**Invalid JSON:**
```json
{
  "error": "Invalid JSON format in request body"
}
```

**Missing field:**
```json
{
  "error": "Missing required field: ip_change"
}
```

**Non-numeric field:**
```json
{
  "error": "Field 'failed_login_attempts' must be numeric (received: str)"
}
```

### **404 Not Found**
```json
{
  "error": "Endpoint not found"
}
```

### **405 Method Not Allowed**
```json
{
  "error": "Method not allowed for this endpoint"
}
```

### **500 Internal Server Error**
```json
{
  "error": "Internal server error"
}
```

---

## 🧪 Testing the API

### Using cURL

**Health Check:**
```bash
curl http://127.0.0.1:5000/health
```

**Make Prediction (Safe):**
```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "failed_login_attempts": 1,
    "login_time_deviation": 0.1,
    "ip_change": 0,
    "device_change": 0,
    "transaction_amount_deviation": 0.2
  }'
```

**Make Prediction (High Risk):**
```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "failed_login_attempts": 5,
    "login_time_deviation": 0.9,
    "ip_change": 1,
    "device_change": 1,
    "transaction_amount_deviation": 0.95
  }'
```

### Using Python (requests)

```python
import requests

url = "http://127.0.0.1:5000/predict"

payload = {
    "failed_login_attempts": 3,
    "login_time_deviation": 0.5,
    "ip_change": 1,
    "device_change": 0,
    "transaction_amount_deviation": 0.8
}

headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)

print(response.status_code)
print(response.json())
```

### Using Postman

1. Create a **POST** request to `http://127.0.0.1:5000/predict`
2. Set header: `Content-Type: application/json`
3. Set body (raw JSON):
   ```json
   {
     "failed_login_attempts": 3,
     "login_time_deviation": 0.5,
     "ip_change": 1,
     "device_change": 0,
     "transaction_amount_deviation": 0.8
   }
   ```
4. Click **Send** and view the response

---

## 📁 Project Structure

```
ai-security-system/
├── api/
│   └── app.py                 # Main Flask application
├── model/
│   ├── train_model.py         # Model training script
│   ├── test.py                # Model testing
│   └── model.pkl              # Trained ML model (not tracked in git)
├── dataset/
│   └── security_data.csv      # Training data
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git exclusion rules
├── .env.example               # Environment variables template
└── README.md                  # This file
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=False

# Model Configuration
MODEL_PATH=model/model.pkl
```

Load in your application:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 📊 Model Information

**Model Type:** Logistic Regression (Binary Classification)  
**Input Features:** 5 numerical features  
**Output Classes:** 2 (0: Safe, 1: High Risk)  
**Accuracy:** [Verify from training logs]  

### Features Explained

- **failed_login_attempts**: Count of failed login attempts (0-10)
- **login_time_deviation**: How unusual the login time is (0-1 scale)
- **ip_change**: Whether IP address changed (0 or 1)
- **device_change**: Whether device changed (0 or 1)
- **transaction_amount_deviation**: How unusual the transaction amount is (0-1 scale)

---

## 🔐 Security Best Practices

✅ **Input Validation** - All inputs are validated  
✅ **Error Handling** - No sensitive info in errors  
✅ **Logging** - Suspicious activity logged  
✅ **Environment Variables** - Sensitive config in .env  
✅ **CORS Ready** - Can be extended with cross-origin support  

---

## 📝 Logging

The API logs important events:

```
INFO - Starting AI Security Risk Prediction API
INFO - Model loaded successfully from model/model.pkl
INFO - Prediction made - Risk Label: 0, Risk Score: 45.23%
ERROR - Unexpected error in /predict endpoint: [error details]
```

Check the console or implement file logging as needed.

---

## 🚀 Deployment

### Local Development
```bash
python api/app.py
```

### Production (using Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 api.app:app
```

### Docker (Optional)
```bash
docker build -t ai-security-api .
docker run -p 5000:5000 ai-security-api
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📧 Support

For issues, questions, or contributions, please contact:
- **Email:** your.email@example.com
- **GitHub Issues:** [Create an issue](https://github.com/yourusername/ai-security-risk-system/issues)

---

## 📚 References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [REST API Best Practices](https://restfulapi.net/)

---

**Last Updated:** February 15, 2026  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
