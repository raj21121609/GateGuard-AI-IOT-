from database import Base, engine
Base.metadata.create_all(bind=engine)
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import requests
import cv2

from pydantic import BaseModel
from datetime import datetime
from database import GuestEntry, SessionLocal

from fastapi.middleware.cors import CORSMiddleware

from fastapi import Form
from database import SessionLocal, Resident

from services.plate_detection import detect_plate
from services.ocr_service import read_plate
from utils.image_utils import preprocess_plate

app = FastAPI()

class IRData(BaseModel):
    event: str
    
class GuestRequest(BaseModel):
    name: str
    vehicle_plate: str
    flat_no: str
    purpose: str

CAMERA_URL = "http://10.124.93.70:8080/shot.jpg"


def capture_image():
    try:
        response = requests.get(CAMERA_URL, timeout=5)

        if response.status_code == 200:
            with open("capture.jpg", "wb") as f:
                f.write(response.content)

            print("📸 Image Captured Successfully!")
        else:
            print("❌ Failed to capture image")

    except Exception as e:
        print("❌ Error:", e)

def process_vehicle():
    capture_image()

    image_path = "capture.jpg"

    plate_img = detect_plate(image_path)
    plate_img_pre = preprocess_plate(plate_img)
    plate_text = read_plate(plate_img_pre)

    if not plate_text:
        image = cv2.imread(image_path)
        plate_text = read_plate(image)

    print("🔍 Detected Plate:", plate_text)

    # 🚪 Decision
    if plate_text and check_access(plate_text):
        print("✅ ACCESS GRANTED")
        return "ALLOW"
    else:
        print("❌ ACCESS DENIED")
        return "DENY"

@app.post("/ir-trigger")
async def ir_trigger(data: IRData):
    print("\n🚨 IR SENSOR TRIGGERED")
    print("Time:", datetime.now())

    decision = process_vehicle()

    return {"decision": decision}

@app.get("/")
def home():
    return {"message": "Backend running 🚀"}

def check_access(plate):
    db = SessionLocal()

    resident = db.query(Resident).filter(
        Resident.vehicle_number == plate
    ).first()

    db.close()

    return resident is not None

@app.post("/add-resident")
def add_resident(
    name: str = Form(...),
    flat_number: str = Form(...),
    vehicle_number: str = Form(...)
):
    db = SessionLocal()

    new_resident = Resident(
        name=name,
        flat_number=flat_number,
        vehicle_number=vehicle_number
    )

    db.add(new_resident)
    db.commit()
    db.close()

    return {"message": "Resident added successfully"}

@app.get("/residents")
def get_residents():
    db = SessionLocal()
    residents = db.query(Resident).all()
    db.close()

    return residents

@app.post("/guest/request")
def request_guest(data: GuestRequest):
    db = SessionLocal()

    guest = GuestEntry(
        guest_name=data.name,
        vehicle_plate=data.vehicle_plate.upper().replace(" ", ""),
        flat_no=data.flat_no,
        purpose=data.purpose,
        approved=False
    )

    db.add(guest)
    db.commit()
    db.refresh(guest)
    db.close()

    return {"status": "request_sent", "guest_id": guest.id}

@app.post("/guest/approve/{guest_id}")
def approve_guest(guest_id: int):
    db = SessionLocal()

    guest = db.query(GuestEntry).filter(GuestEntry.id == guest_id).first()

    if not guest:
        return {"error": "Not found"}

    guest.approved = True
    guest.approved_at = datetime.utcnow()

    db.commit()
    db.close()

    return {"status": "approved"}

@app.post("/guest/deny/{guest_id}")
def deny_guest(guest_id: int):
    db = SessionLocal()

    guest = db.query(GuestEntry).filter(GuestEntry.id == guest_id).first()

    if not guest:
        return {"error": "Not found"}

    guest.approved = False

    db.commit()
    db.close()

    return {"status": "denied"}

@app.get("/guest")
def get_guests(approved: bool = None):
    db = SessionLocal()

    query = db.query(GuestEntry)

    if approved is not None:
        query = query.filter(GuestEntry.approved == approved)

    guests = query.all()
    db.close()

    return guests

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
