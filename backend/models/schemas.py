from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime

Area = Literal["waiting_area","doctor_room","operation_theatre","patient_room",
               "testing_room","medicine_storage"]

class SensorPoint(BaseModel):
    id: int
    area: Area
    metric: str
    value: float
    unit: str = Field(default="")
    ts: datetime = Field(default_factory=datetime.utcnow)

class BulkSensorPayload(BaseModel):
    points: List[SensorPoint]

class AlertOut(BaseModel):
    area: Area
    severity: Literal["INFO","WARN","ALERT"]
    message: str
    ts: datetime
    level:str

class ReportOut(BaseModel):
    summary: str
    recommendations: list[str]
    ts: datetime
