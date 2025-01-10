from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import qrcode
import uuid
from io import BytesIO
from fastapi.responses import StreamingResponse
import os
from fastapi.responses import JSONResponse

app = FastAPI()

# In-memory database
providers_db = {}

# Directory to save generated QR codes
QR_CODE_DIR = "qrcodes"
os.makedirs(QR_CODE_DIR, exist_ok=True)


# Pydantic models
class Product(BaseModel):
    category: str
    title: str
    description: str
    price: float


class Provider(BaseModel):
    business_name: str
    email: str
    phone_number: str


def generate_qr_code(data: str, filename: str):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)  # Use the redirect URL as data
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")

    img_path = os.path.join(QR_CODE_DIR, filename)
    img.save(img_path)

    return img_path




@app.post("/register/")
async def register_provider(provider: Provider):
    # Check if the provider is already registered
    for existing_provider in providers_db.values():
        if existing_provider["email"] == provider.email:
            raise HTTPException(status_code=400, detail="Provider already registered")

    # Generate a unique ID for the provider
    provider_id = str(uuid.uuid4())

    # Save the provider in the database
    providers_db[provider_id] = {
        "provider_id": provider_id,
        "business_name": provider.business_name,
        "email": provider.email,
        "phone_number": provider.phone_number,
        "products": [],
    }

    # Create the URL for the provider's page
    provider_url = f" http://127.0.0.1:8000/provider/{provider_id}"  # Replace with your domain

    # Generate a QR code with the provider URL
    qr_code_filename = f"{provider.business_name}_qr.png"
    qr_code_path = generate_qr_code(provider_url, qr_code_filename)

    return {
        "message": "Provider registered successfully",
        "provider_id": provider_id,
        "qr_code_path": qr_code_path,
        "provider_url": provider_url,
    }



@app.post("/add-product/{provider_id}")
async def add_product(provider_id: str, product: Product):
    # Check if the provider exists
    if provider_id not in providers_db:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Add the product to the provider's list
    providers_db[provider_id]["products"].append(product.dict())

    return {"message": "Product added successfully"}


@app.get("/providers/")
async def get_all_providers():
    # Return all registered providers and their products
    return providers_db




@app.get("/provider/{provider_id}")
async def get_provider_details(provider_id: str):
    # Check if the provider exists
    if provider_id not in providers_db:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Fetch provider details
    provider_data = providers_db[provider_id]
    return JSONResponse(content={
        "provider": {
            "provider_id": provider_id,
            "business_name": provider_data["business_name"],
            "email": provider_data["email"],
            "phone_number": provider_data["phone_number"],
        },
        "products": provider_data["products"],
    })

