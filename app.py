from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

app = FastAPI(title="CareGuide Triage API", version="1.0.0")

class TriageRequest(BaseModel):
    age: int = Field(ge=0)
    symptoms: str
    duration: str  # e.g., "2 days"

class TriageResponse(BaseModel):
    band: str  # self_care | see_gp | urgent_care | emergency
    redFlags: List[str] = []

@app.post("/triage", response_model=TriageResponse)
def check_symptoms(req: TriageRequest):
    text = (req.symptoms or "").lower()
    red_flags = []
    band = "self_care"

    # Simple, safe IF–THEN rules (expand later as you wish)
    if any(k in text for k in ["chest pain", "severe chest", "pressure in chest"]) or \
       any(k in text for k in ["shortness of breath", "trouble breathing"]) or \
       any(k in text for k in ["stroke", "face droop", "slurred speech"]) or \
       "suicidal" in text:
        band = "emergency"
        if "chest" in text: red_flags.append("Possible cardiac symptoms")
        if "breath" in text: red_flags.append("Respiratory distress")
        if any(k in text for k in ["stroke","slurred","droop"]): red_flags.append("Neurological red flag")
        if "suicidal" in text: red_flags.append("Mental health crisis")
    elif any(k in text for k in ["high fever", "102", "39°", "39c"]) or \
         any(k in text for k in ["severe pain", "uncontrolled bleeding", "fainting"]):
        band = "urgent_care"
        red_flags.append("Acute severe symptom")
    elif any(k in text for k in ["persistent", "worsening", "lasting more than", "> 1 week"]):
        band = "see_gp"

    if req.age < 1 and "fever" in text:
        band = "urgent_care"
        red_flags.append("Infant with fever")

    return TriageResponse(band=band, redFlags=red_flags)

@app.get("/health")
def health():
    return {"ok": True}
