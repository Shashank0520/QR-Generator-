import os
import uuid
import qrcode
import requests
from io import BytesIO 
from qrcode.constants import ERROR_CORRECT_H
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse

app = FastAPI()

from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="static", html=True), name="static")


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://127.0.0.1:5500"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Function to generate QR code image
# -------------------------------
def create_qr_image(data: str) -> BytesIO:
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    
    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf


# -------------------------------
# IMAGE → QR (hosted online)
# -------------------------------
@app.post("/generate-qr-image/")
async def generate_qr_image(file: UploadFile = File(...)):
    # Allowed image types
    allowed_exts = [".jpg", ".jpeg", ".png"]
    file_ext = os.path.splitext(file.filename)[-1].lower()

    if file_ext not in allowed_exts:
        return {"error": "Only image files (.jpg, .jpeg, .png) are supported."}

    temp_name = f"temp_{uuid.uuid4().hex}{file_ext}"
    with open(temp_name, "wb") as f:
        f.write(await file.read())

    try:
        # Upload to GoFile
        with open(temp_name, "rb") as f:
            files = {"file": (file.filename, f)}
            response = requests.post("https://store1.gofile.io/uploadFile", files=files)

        os.remove(temp_name)

        if response.status_code != 200:
            return {"error": "Failed to upload image online."}

        data = response.json()
        uploaded_url = data["data"]["downloadPage"]

        # Generate QR
        buf = create_qr_image(uploaded_url)
        return StreamingResponse(
            buf,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"attachment; filename=qr_image_{uuid.uuid4().hex}.jpg"
            },
        )

    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}


# -------------------------------
# ANY FILE → QR (hosted online)
# -------------------------------
@app.post("/generate-qr-file/")
async def generate_qr_file(file: UploadFile = File(...)):
    temp_name = f"temp_{uuid.uuid4().hex}_{file.filename}"
    with open(temp_name, "wb") as f:
        f.write(await file.read())

    try:
        # Upload to GoFile
        with open(temp_name, "rb") as f:
            files = {"file": (file.filename, f)}
            response = requests.post("https://store1.gofile.io/uploadFile", files=files)

        os.remove(temp_name)

        if response.status_code != 200:
            return {"error": f"Upload failed with code {response.status_code}"}

        data = response.json()
        uploaded_url = data["data"]["downloadPage"]

        buf = create_qr_image(uploaded_url)
        return StreamingResponse(
            buf,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"attachment; filename=qr_{uuid.uuid4().hex}.jpg"
            },
        )

    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}


# -------------------------------
# LINK → QR
# -------------------------------
@app.post("/generate-qr-text/")
async def generate_qr_text(link: str = Form(...)):
    if not link.startswith(("http://", "https://")):
        return {"error": "Please enter a valid URL (must start with http:// or https://)"}

    buf = create_qr_image(link)
    return StreamingResponse(
        buf,
        media_type="image/jpeg",
        headers={
            "Content-Disposition": f"attachment; filename=qr_link_{uuid.uuid4().hex}.jpg"
        },
    )


