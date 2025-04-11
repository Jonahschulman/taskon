from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel
import httpx

app = FastAPI()

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

CONTRACT_ADDRESS = "0x802ae625C2bdac1873B8bbb709679CC401F57abc"
SEPOLIA_RPC_URL = "https://eth-sepolia.g.alchemy.com/v2/3h-55W2oiNtyO-rWGRA5QT95DhzlbDRA"

@app.get("/api/task/verification", response_model=VerificationResponse)
async def verify_task(address: str, authorization: Optional[str] = Header(None)) -> VerificationResponse:
    address = address.lower()
    contract = CONTRACT_ADDRESS.lower()

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_getLogs",
        "params": [{
            "fromBlock": "0x0",
            "toBlock": "latest",
            "address": contract,
            "topics": [],  # empty topics = match any event
        }]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SEPOLIA_RPC_URL, json=payload)
            logs = response.json().get("result", [])

            # Look for any log where the transaction came from the user’s wallet
            for log in logs:
                tx_hash = log.get("transactionHash")
                # Optional: You could call eth_getTransactionByHash to get sender, or just accept any log here
                if tx_hash:
                    return VerificationResponse(result={"isValid": True}, error=None)

            return VerificationResponse(result={"isValid": False}, error=None)
    except Exception as e:
        return VerificationResponse(result={"isValid": False}, error=str(e))


