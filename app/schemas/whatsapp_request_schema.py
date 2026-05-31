from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class WhatsAppRequestBase(BaseModel):
    request_phone_number: str
    message_id: str
    json_summary: Any
    status: str = "Pending"
    rejection_reason: Optional[str] = None
class WhatsAppRequestCreate(WhatsAppRequestBase):
    pass

class WhatsAppRequestUpdate(BaseModel):
    status: str
    rejection_reason: Optional[str] = None

class WhatsAppRequestOut(WhatsAppRequestBase):
    id_request: int
    id_business: int
    created_at: datetime

    class Config:
        from_attributes = True
