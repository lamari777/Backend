from fastapi import APIRouter, Request

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

@router.post("/webhook")
async def twilio_webhook(request: Request):
    try:
        form_data = await request.form()
        telefono_cliente = form_data.get('From', '')
        mensaje_cliente = form_data.get('Body', '')
        print(f"De: {telefono_cliente}")
        print(f"Mensaje: {mensaje_cliente}")
        return {"status": "ok"}
    except Exception as e:
        print(f"Error en webhook: {e}")
        return {"status": "error", "detail": str(e)}