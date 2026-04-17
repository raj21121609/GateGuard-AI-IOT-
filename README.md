# 🚧 GateGuard AI – Smart Watchman IoT

An intelligent automated gate security system that uses **AI-based number plate detection**, **OCR**, and **IoT integration** to manage vehicle access in residential societies or secure areas.

---

## 📌 Overview

GateGuard AI replaces manual gatekeepers with a smart system that:

- Detects vehicles using camera input
- Extracts number plates using AI (YOLOv8 + EasyOCR)
- Verifies vehicle against database
- Automatically allows or denies entry
- Logs all entries for monitoring

---

## 🧠 Features

- 🚗 Automatic Vehicle Detection  
- 🔍 Number Plate Recognition (YOLOv8 + EasyOCR)  
- 🏠 Resident Vehicle Verification  
- 🎟️ Guest Entry via QR / Approval Flow  
- 📡 ESP32 IoT Integration (IR Sensor + Gate Control)  
- 📊 Entry Logging System  
- 🌐 Backend API for decision making  

---

## 🏗️ System Architecture

Camera → Backend (YOLO + OCR) → Database Check → Decision
↓
ESP32 Gate Control


---

## ⚙️ Tech Stack

### 🔹 Backend
- Python  
- Django / FastAPI  
- OpenCV  
- YOLOv8  
- EasyOCR  

### 🔹 IoT
- ESP32  
- IR Sensor  
- Servo Motor (SG90)  
- WiFi (HTTP communication)  

### 🔹 Database
- PostgreSQL / Supabase  

### 🔹 Frontend (Optional)
- Flutter  

---

## 🔌 Hardware Setup

- ESP32 connected to:
  - IR Sensor (vehicle detection)  
  - Servo Motor (gate control)  
- ESP32 sends HTTP requests to backend when vehicle is detected  

---

## 🚀 API Endpoints

### 🔹 Detect Vehicle

**POST** `/detect-vehicle`

Uploads an image and returns gate decision.

#### Request:
- Image file (vehicle photo)

#### Response:
```json
{
  "status": "allowed",
  "plate_number": "MH12AB1234",
  "type": "resident"
}
🔁 Workflow
Vehicle arrives → IR sensor triggers ESP32
ESP32 sends request to backend
Backend:
Detects number plate using YOLO
Extracts text using OCR
Checks database
Decision:
✅ Resident → Gate opens
⏳ Guest → Approval required
❌ Unknown → Denied
Entry is logged
📦 Installation
🔹 Backend Setup
git clone https://github.com/your-repo/GateGuard-AI-IOT.git
cd GateGuard-AI-IOT

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt

Run server:

python manage.py runserver
# OR
uvicorn main:app --reload
🔹 ESP32 Setup
Open Arduino IDE
Install ESP32 board support
Upload code with:
WiFi credentials
Backend server URL

Example:

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";
const char* serverUrl = "http://YOUR_SERVER_IP:8000/ir-trigger";
🛠️ Future Improvements
📷 Live camera streaming
📱 Mobile app notifications
🔐 Face recognition integration
☁️ Cloud deployment (AWS / Render)
📊 Dashboard analytics
🤝 Contributing

Contributions are welcome!

Fork the repo
Create a new branch
Commit your changes
Open a pull request
📜 License

This project is licensed under the MIT License.

👨‍💻 Author

Raj
IoT + AI Developer


---

If you want next level polish, I can:
- add **badges (build, license, tech icons)**  
- include **architecture diagram image (looks 🔥 on GitHub)**  
- or tailor this for **hackathon judging (problem → solution → impact)**