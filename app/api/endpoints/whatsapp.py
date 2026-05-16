import os
from fastapi import APIRouter, Request
from openai import AsyncOpenAI

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])
client = AsyncOpenAI(
    api_key=os.environ.get("GROQ_APIKEY"),
    base_url="https://api.groq.com/openai/v1"
)

async def es_un_pedido(texto: str) -> bool:
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Eres un clasificador de mensajes de WhatsApp" + 
                "para un negocio. Si el texto parece ser un encargo, pedido, reserva o solicitud de " +
                "productos, responde ÚNICAMENTE con la palabra 'SI'. Si es un simple saludo, duda, u otra " +
                "cosa, responde ÚNICAMENTE con la palabra 'NO'."},
                {"role": "user", "content": texto}
            ],
            temperature=0,
            max_tokens=3
        )
        respuesta_ia = response.choices[0].message.content.strip().upper()
        return "SI" in respuesta_ia
    except Exception as e:
        print(f"Error llamando a Groq: {e}", flush=True)
        return False

@router.post("/webhook")
async def twilio_webhook(request: Request):
    try:
        form_data = await request.form()
        telefono_cliente = form_data.get('From', '')
        mensaje_cliente = form_data.get('Body', '')
        
        print(f"telefono: {telefono_cliente} ", flush=True)
        print(f"mensaje: {mensaje_cliente}", flush=True)
        es_pedido = await es_un_pedido(mensaje_cliente)
        
        if es_pedido:
            print("Es un pedido.", flush=True)
        else:
            print("No es un pedido.", flush=True)
        
        return {"status": "ok"}
    except Exception as e:
        print(f"Error en webhook: {e}", flush=True)
        return {"status": "error", "detail": str(e)}
