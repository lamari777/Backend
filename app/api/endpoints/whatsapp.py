from fastapi import APIRouter, Request
router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])
@router.post("/webhook")
async def twilio_webhook(request: Request):
    form_data = await request.form()
    telefono_cliente = form_data.get('From', '')
    mensaje_cliente = form_data.get('Body', '')
    print(f"De: {telefono_cliente}")
    print(f"Mensaje: {mensaje_cliente}")
    return {"status": "ok"}