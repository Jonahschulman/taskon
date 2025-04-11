from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel

app = FastAPI(
    title="TaskOn Verification API Demo",
    description="A demo API for TaskOn task verification integration",
    version="1.0.0",
)

# Add CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class VerificationResponse(BaseModel):
    result: dict = {"isValid": bool}
    error: Optional[str] = None

DEMO_COMPLETED_TASKS = {
    # Demo wallet addresses
    "0xd5045deea369d64ab7efab41ad18b82eeabcdefg",
    "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    # Demo social accounts
    "taskonxyz",
    "1084460817220641111",  # Discord ID
    "6881505111",  # Telegram ID
    "demo@taskon.xyz"
}

@app.get(
    "/api/task/verification",
    response_model=VerificationResponse,
    summary="Verify Task Completion",
    description="Verify if a user has completed the task based on their wallet address or social media ID",
)
async def verify_task(
    address: str,
    authorization: Optional[str] = Header(None)
) -> VerificationResponse:
    # Convert address to lowercase for case-insensitive comparison
    address = address.lower()
    
    # Demo implementation - check if address exists in demo completed tasks
    is_valid = address in DEMO_COMPLETED_TASKS
    
    return VerificationResponse(result={"isValid": is_valid}, error=None)

@app.get("/")
async def root():
    return {"message": "Welcome to TaskOn Verification API Demo"}