from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal

router = APIRouter(prefix="/control", tags=["control"])

class ControlCmd(BaseModel):
    area: Literal["waiting_area","doctor_room","operation_theatre","patient_room","testing_room","medicine_storage"]
    device: Literal["light","ac","fan","dehumidifier","oxygen"]
    action: Literal["ON","OFF","AUTO"]

@router.post("/device")
def control_device(cmd: ControlCmd):
    # stub: in real world, publish to MQTT or device API
    return {"status": "accepted", "details": cmd.dict()}

@router.post("/control/device")
async def control_device(device: str, action: str):
    return {
        "device": device,
        "action": action,
        "status": "success"
    }