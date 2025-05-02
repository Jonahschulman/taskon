from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel
import httpx

app = FastAPI(
    title="TaskOn Verification API Demo",
    description="Verifies if a user has interacted with a Sepolia contract (e.g. placed an order)",
    version="1.0.0"
)

# Allow all origins/methods for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VerificationResponse(BaseModel):
    result: dict = {"isValid": bool}
    error: Optional[str] = None

# Update with your contract + Alchemy RPC URL
CONTRACT_ADDRESS = "0x802ae625C2bdac1873B8bbb709679CC401F57abc"
SEPOLIA_RPC_URL = "https://eth-sepolia.g.alchemy.com/v2/3h-55W2oiNtyO-rWGRA5QT95DhzlbDRA"

@app.get("/api/task/verification", response_model=VerificationResponse)
async def verify_task(address: str, authorization: Optional[str] = Header(None)) -> VerificationResponse:
    address = address.lower()
    contract = CONTRACT_ADDRESS.lower()

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getAssetTransfers",
        "params": [{
            "fromAddress": address,
            "toAddress": contract,
            "category": ["external", "internal"],
            "excludeZeroValue": False,
            "withMetadata": False,
            "maxCount": "0x64",
            "fromBlock": "0x7d7bb0",
            "toBlock": "latest"
        }]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SEPOLIA_RPC_URL, json=payload)
            result = response.json().get("result", {})
            transfers = result.get("transfers", [])

            is_valid = len(transfers) > 0
            return VerificationResponse(result={"isValid": is_valid}, error=None)

    except Exception as e:
        return VerificationResponse(result={"isValid": False}, error=str(e))

@app.get("/")
async def root():
    return {"message": "TaskOn Verification API is running."}

