from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel
import os
import httpx

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

CONTRACT_ADDRESS = "0x802ae625C2bdac1873B8bbb709679CC401F57abc"
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")
SEPOLIA_RPC_URL = f"https://eth-sepolia.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

@app.get(
    "/api/task/verification",
    response_model=VerificationResponse,
    summary="Verify Task Completion",
    description="Verify if a user has placed an order on the Sepolia contract",
)
async def verify_task(
    address: str,
    authorization: Optional[str] = Header(None)
) -> VerificationResponse:
    address = address.lower()

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getAssetTransfers",
        "params": [{
            "fromAddress": address,
            "toAddress": CONTRACT_ADDRESS,
            "category": ["external", "erc20", "erc721", "erc1155"],
            "withMetadata": False,
            "excludeZeroValue": True,
            "maxCount": "0x64"
        }]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(SEPOLIA_RPC_URL, json=payload)
            transfers = response.json().get("result", {}).get("transfers", [])
            is_valid = len(transfers) > 0
            return VerificationResponse(result={"isValid": is_valid}, error=None)
        except Exception as e:
            return VerificationResponse(result={"isValid": False}, error=str(e))
