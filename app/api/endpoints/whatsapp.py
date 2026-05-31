import os
import json
import asyncpg
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from openai import AsyncOpenAI

from app.db.database import get_pool
from app.api.dependencies import get_db, get_current_business
from app.repositories.business_repo import get_business_by_phone
from app.repositories.material_repo import get_materials_by_business
from app.schemas.whatsapp_request_schema import WhatsAppRequestCreate, WhatsAppRequestUpdate, WhatsAppRequestOut
from app.repositories.whatsapp_request_repo import (
    create_whatsapp_request,
    get_whatsapp_requests_by_business,
    update_whatsapp_request_status
)

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])
client = AsyncOpenAI(
    api_key=os.environ.get("GROQ_APIKEY"),
    base_url="https://api.groq.com/openai/v1"
)


@router.get("/pedidos/{id_business}", response_model=list[WhatsAppRequestOut])
async def obtener_pedidos(
    id_business: int,
    conn: asyncpg.Connection = Depends(get_db)
):
    requests = await get_whatsapp_requests_by_business(conn, id_business)
    for r in requests:
        if isinstance(r.get("json_summary"), str):
            try:
                r["json_summary"] = json.loads(r["json_summary"])
            except Exception:
                pass
    return requests


async def es_un_pedido(texto: str) -> bool:
    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Clasifica si el mensaje es un pedido/encargo/reserva de productos. "
                        "Responde ÚNICAMENTE 'SI' o 'NO'."
                    )
                },
                {"role": "user", "content": texto}
            ],
            temperature=0,
            max_tokens=2
        )
        respuesta_ia = response.choices[0].message.content.strip().upper()
        return "SI" in respuesta_ia
    except Exception as e:
        print(f"Error llamando a Groq (es_un_pedido): {e}", flush=True)
        return False


async def resolver_productos_con_catalogo(mensaje: str, catalogo: list[str]) -> list[dict]:
    catalogo_texto = ", ".join(catalogo)

    prompt_sistema = (
        "Eres un asistente de gestión de pedidos. Tu tarea es:\n"
        "1. Leer el mensaje de un cliente que hace un pedido.\n"
        "2. Extraer cada producto que pide y su cantidad (1 si no se indica).\n"
        "3. Para cada producto pedido, buscar en el CATÁLOGO proporcionado qué producto o productos "
        "encajan mejor, teniendo en cuenta sinónimos, abreviaciones, errores ortográficos y variantes "
        "(por ejemplo 'cocacola', 'coca cola' y 'Coca-Cola' son lo mismo; "
        "'normal' o 'clásica' descarta las versiones 'Zero' o '0').\n"
        "4. Devolver ÚNICAMENTE un JSON válido (sin texto adicional) con este formato exacto:\n"
        "[\n"
        "  {\"solicitado\": \"<texto del cliente>\", \"cantidad\": <número>, "
        "\"coincidencias\": [\"<nombre exacto del catálogo>\", ...]}\n"
        "]\n"
        "- Si un producto no tiene ninguna coincidencia en el catálogo, pon 'coincidencias': [].\n"
        "- Si hay una coincidencia clara y única, pon solo ese nombre.\n"
        "- Si hay ambigüedad (varias opciones igualmente válidas), ponlas todas.\n"
        "- Usa SIEMPRE los nombres exactamente como aparecen en el catálogo.\n\n"
        f"CATÁLOGO DISPONIBLE:\n{catalogo_texto}"
    )

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user",   "content": mensaje}
            ],
            temperature=0,
            max_tokens=500
        )
        contenido = response.choices[0].message.content.strip()
        inicio = contenido.find("[")
        fin = contenido.rfind("]") + 1
        if inicio == -1 or fin == 0:
            print(f"La IA no devolvió un JSON de lista válido: {contenido}", flush=True)
            return []
        items = json.loads(contenido[inicio:fin])
        return items if isinstance(items, list) else []
    except Exception as e:
        print(f"Error llamando a Groq (resolver_productos): {e}", flush=True)
        return []


async def generar_respuesta_aclaracion(items: list[dict], nombre_negocio: str) -> str:
    problemas = []
    for item in items:
        solicitado = item.get("solicitado", "")
        coincidencias = item.get("coincidencias", [])
        if len(coincidencias) > 1:
            opciones = ", ".join(f"'{c}'" for c in coincidencias)
            problemas.append(f"- Para '{solicitado}' tenemos varias opciones: {opciones}.")
        elif len(coincidencias) == 0:
            problemas.append(f"- No hemos encontrado '{solicitado}' en nuestro catálogo.")
            
    if not problemas:
        return ""
        
    texto_problemas = "\n".join(problemas)
    
    prompt_sistema = (
        f"Eres el asistente virtual por WhatsApp del negocio '{nombre_negocio}'. "
        "Un cliente ha hecho un pedido, pero algunos productos no están claros. "
        "Redacta un mensaje amable, directo y corto para el cliente, explicándole las dudas que tenemos "
        "y preguntándole qué opciones prefiere de las que le indicamos. "
        "Muestra las opciones de forma clara. Si algo no existe en el catálogo, díselo educadamente.\n"
        "IMPORTANTE: Devuelve ÚNICAMENTE el texto del mensaje que se enviará por WhatsApp al cliente, sin comillas adicionales ni texto introductorio tuyo."
    )
    
    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Esta es la información de los productos dudosos:\n{texto_problemas}"}
            ],
            temperature=0.3,
            max_tokens=250
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generando aclaración con IA: {e}", flush=True)
        return "Hola, hemos recibido tu pedido pero tenemos dudas con algunos productos. ¿Podrías confirmarnos exactamente qué deseas de nuestro catálogo?"


@router.post("/webhook")
async def twilio_webhook(request: Request):
    try:
        form_data = await request.form()
        telefono_cliente = form_data.get("From", "")
        mensaje_cliente = form_data.get("Body", "")
        numero_twilio = form_data.get("To", "")
        message_id = form_data.get("MessageSid", "")

        print(f"De: {telefono_cliente} | Para: {numero_twilio}", flush=True)
        print(f"Mensaje: {mensaje_cliente}", flush=True)

        pool = get_pool()
        async with pool.acquire() as conn:
            negocio = await get_business_by_phone(conn, numero_twilio)

            if not negocio:
                print(f"No se encontró ningún negocio con el número: {numero_twilio}", flush=True)
                return {"status": "ok"}

            id_business = negocio["id_business"]
            print(f"Negocio identificado: {negocio['name_business']} (id={id_business})", flush=True)

            es_pedido = await es_un_pedido(mensaje_cliente)
            if not es_pedido:
                print("No es un pedido.", flush=True)
                return {"status": "ok"}

            print("Es un pedido.", flush=True)

            materiales = await get_materials_by_business(conn, id_business)
            if not materiales:
                print("El negocio no tiene productos en el catálogo.", flush=True)
                return {"status": "ok"}

            catalogo_nombres = [m["material_name"] for m in materiales]
            print(f"Catálogo cargado: {len(catalogo_nombres)} productos.", flush=True)

            items_resueltos = await resolver_productos_con_catalogo(mensaje_cliente, catalogo_nombres)

            if not items_resueltos:
                print("No se pudieron resolver los productos del mensaje.", flush=True)
                return {"status": "ok"}

            print(f"Resultado del matching: {items_resueltos}", flush=True)

            for item in items_resueltos:
                solicitado  = item.get("solicitado", "")
                cantidad    = item.get("cantidad", 1)
                coincidencias = item.get("coincidencias", [])

                if len(coincidencias) == 0:
                    print(f"Producto '{solicitado}' (x{cantidad}) No encontrado.", flush=True)
                elif len(coincidencias) == 1:
                    print(f"Producto '{solicitado}' (x{cantidad}) Coincidencia: '{coincidencias[0]}'", flush=True)
                else:
                    opciones = ", ".join(f'"{n}"' for n in coincidencias)
                    print(f"Producto '{solicitado}' (x{cantidad}) Opciones: {opciones}", flush=True)

            tiene_no_encontrado = any(len(item.get("coincidencias", [])) == 0 for item in items_resueltos)
            tiene_ambiguo = any(len(item.get("coincidencias", [])) > 1 for item in items_resueltos)

            req_data = WhatsAppRequestCreate(
                request_phone_number=telefono_cliente.replace("whatsapp:", ""),
                message_id=message_id,
                json_summary=items_resueltos,
                status="Pending",
                rejection_reason=None
            )
            try:
                saved = await create_whatsapp_request(conn, id_business, req_data)
                print(f"Pedido guardado en BD con id={saved.get('id_request')}", flush=True)
            except Exception as db_err:
                print(f"ERROR al guardar pedido en BD: {db_err}", flush=True)

            if tiene_ambiguo or tiene_no_encontrado:
                print("Generando respuesta de aclaración con IA...", flush=True)
                respuesta_texto = await generar_respuesta_aclaracion(items_resueltos, negocio['name_business'])
                xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
                <Response>
                    <Message>{respuesta_texto}</Message>
                </Response>"""
                return Response(content=xml_response, media_type="application/xml")

        return {"status": "ok"}

    except Exception as e:
        import traceback
        print(f"Error en webhook: {e}", flush=True)
        print(traceback.format_exc(), flush=True)
        return {"status": "error", "detail": str(e)}


@router.patch("/pedidos/{id_request}", response_model=WhatsAppRequestOut, summary="Actualizar el estado de un pedido de WhatsApp")
async def actualizar_estado_pedido(
    id_request: int,
    request_update: WhatsAppRequestUpdate,
    conn: asyncpg.Connection = Depends(get_db),
    current_payload: dict = Depends(get_current_business)
):
    id_business = int(current_payload["sub"])
    updated = await update_whatsapp_request_status(
        conn,
        id_business,
        id_request,
        request_update.status,
        request_update.rejection_reason
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido de WhatsApp no encontrado o no pertenece a tu negocio"
        )
    if isinstance(updated.get("json_summary"), str):
        try:
            updated["json_summary"] = json.loads(updated["json_summary"])
        except Exception:
            pass
    return updated
