"""
services/gdocs.py — Servicio de Google Docs para Reactivos.

Encapsula la interacción con Google Docs API y Google Drive API
para crear/actualizar documentos de reactivos diarios.
"""
import os
import logging
from datetime import datetime, timezone

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# Nombre de la carpeta en Google Drive
FOLDER_NAME = "Reactivos LGC"


def get_credentials(user):
    """
    Construye google.oauth2.credentials.Credentials a partir de los tokens
    del usuario. Refresca automáticamente si están expirados.

    Retorna Credentials o None si no hay tokens.
    """
    if not user.google_refresh_token:
        return None

    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    )

    # Refrescar si expiró
    if not creds.valid:
        try:
            creds.refresh(Request())
            # Actualizar tokens en BD
            from models import db
            user.google_access_token = creds.token
            if creds.expiry:
                user.google_token_expires_at = creds.expiry.replace(
                    tzinfo=timezone.utc
                )
            db.session.commit()
            logger.info("Google tokens refreshed for user %s", user.email)
        except Exception as e:
            logger.error("Error refreshing Google tokens for %s: %s", user.email, e)
            return None

    return creds


def _get_services(creds):
    """Construye servicios de Google Docs y Drive."""
    docs = build("docs", "v1", credentials=creds, cache_discovery=False)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    return docs, drive


def ensure_folder(drive_service):
    """
    Busca la carpeta 'Reactivos LGC' en Google Drive.
    Si no existe, la crea. Retorna el folder_id.
    """
    query = (
        "mimeType = 'application/vnd.google-apps.folder' "
        "and name = '{}' "
        "and trashed = false"
    ).format(FOLDER_NAME)

    results = drive_service.files().list(
        q=query, spaces="drive", fields="files(id, name)", pageSize=1
    ).execute()

    files = results.get("files", [])
    if files:
        return files[0]["id"]

    # Crear carpeta
    folder_meta = {
        "name": FOLDER_NAME,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = drive_service.files().create(
        body=folder_meta, fields="id"
    ).execute()
    logger.info("Created Google Drive folder '%s': %s", FOLDER_NAME, folder["id"])
    return folder["id"]


def find_doc_for_date(drive_service, folder_id, date_str):
    """
    Busca un doc con nombre 'Reactivos — {date_str}' dentro de la carpeta.
    date_str formato: "DD/MM/AAAA"
    Retorna el doc_id o None.
    """
    doc_name = "Reactivos \u2014 {}".format(date_str)
    query = (
        "name = '{}' "
        "and '{}' in parents "
        "and mimeType = 'application/vnd.google-apps.document' "
        "and trashed = false"
    ).format(doc_name.replace("'", "\\'"), folder_id)

    results = drive_service.files().list(
        q=query, spaces="drive", fields="files(id, name)", pageSize=1
    ).execute()

    files = results.get("files", [])
    return files[0]["id"] if files else None


def _format_cabecera(date_str, hora, cabecera_data, user):
    """
    Formatea la cabecera del día como texto plano para el Google Doc.
    cabecera_data es un dict con los datos Calendaria calculados en JS.
    """
    lines = []
    lines.append("=" * 50)
    lines.append("REACTIVOS \u2014 {}".format(date_str))
    lines.append("=" * 50)
    lines.append("")

    # Datos del usuario
    lines.append("Usuario: {} ({})".format(user.nombre, user.email))
    if user.birth_date:
        lines.append("Nacimiento: {}".format(user.birth_date.strftime("%d/%m/%Y")))
    lines.append("")

    # Datos Calendaria
    if cabecera_data:
        ds = cabecera_data.get("ds", "")
        if ds:
            lines.append("Dia Solar: {}".format(ds))

        ds_nativo = cabecera_data.get("dsNativo")
        if ds_nativo is not None:
            lines.append("Dia Solar Nativo: {}".format(ds_nativo))

        ddv = cabecera_data.get("ddv")
        if ddv is not None:
            lines.append("Dias de Vida: {}".format(ddv))

        # Posicion Calendaria
        if cabecera_data.get("esAnillo"):
            dia_anillo = cabecera_data.get("diaAnillo", "")
            total_anillo = cabecera_data.get("totalAnillo", "")
            lines.append("Posicion: Anillo de Fuego {}/{}".format(
                dia_anillo, total_anillo
            ))
        else:
            pos = cabecera_data.get("pos", "")
            cuad = cabecera_data.get("cuad", "")
            paso = cabecera_data.get("paso", "")
            mem = cabecera_data.get("mem", "")
            v_abs = cabecera_data.get("vAbs", "")
            pos_str = "Posicion: V{} - {}/16 - {} - {}".format(
                v_abs, pos, cuad, paso
            )
            if mem:
                pos_str += " - {}".format(mem)
            lines.append(pos_str)

        # Aparato
        ap_num = cabecera_data.get("apNum", "")
        fase_name = cabecera_data.get("faseName", "")
        apos = cabecera_data.get("apos", "")
        aneg = cabecera_data.get("aneg", "")
        if ap_num:
            lines.append("Aparato: #{} - {} - Dia {}/1461".format(
                ap_num, fase_name, apos
            ))
            anu_ap = cabecera_data.get("anuAp", "")
            lines.append("  +{} -{} Anu: {}".format(apos, aneg, anu_ap))

        # Dia del Ano
        doy = cabecera_data.get("doy", "")
        total = cabecera_data.get("total", "")
        frc_pos = cabecera_data.get("frcPos", "")
        frc_neg = cabecera_data.get("frcNeg", "")
        anu_year = cabecera_data.get("anuAno", "")
        if doy:
            lines.append("Dia del Ano: {}/{} (+{} -{} Anu: {})".format(
                doy, total, frc_pos, frc_neg, anu_year
            ))

        # Cuarentena Global
        cuarentena = cabecera_data.get("cuarentena", {})
        qi = cuarentena.get("qi", 0)
        if qi:
            q_dpos = cuarentena.get("qDpos", "")
            brick_idx = cuarentena.get("brickIdx", "")
            brick_day = cuarentena.get("brickDay", "")
            lines.append("Cuarentena Global: #{} - Dia {}/39 - Ladrillo {} ({}/3)".format(
                qi, q_dpos, brick_idx, brick_day
            ))

    lines.append("")
    lines.append("-" * 50)
    lines.append("")

    return "\n".join(lines)


def create_doc_with_header(docs_service, drive_service, folder_id,
                           date_str, hora, cabecera_data, user):
    """
    Crea un Google Doc nuevo con la cabecera del día.
    Retorna el doc_id.
    """
    doc_name = "Reactivos \u2014 {}".format(date_str)

    # Crear el documento
    doc = docs_service.documents().create(body={"title": doc_name}).execute()
    doc_id = doc["documentId"]

    # Mover a la carpeta
    drive_service.files().update(
        fileId=doc_id,
        addParents=folder_id,
        removeParents="root",
        fields="id, parents",
    ).execute()

    # Insertar cabecera
    header_text = _format_cabecera(date_str, hora, cabecera_data, user)

    requests = [
        {
            "insertText": {
                "location": {"index": 1},
                "text": header_text,
            }
        }
    ]
    docs_service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()

    logger.info("Created Google Doc '%s': %s", doc_name, doc_id)
    return doc_id


def append_reactivo(docs_service, doc_id, hora, texto, tags=None):
    """
    Agrega un reactivo al final del documento con timestamp y tags.
    """
    # Obtener longitud actual del documento
    doc = docs_service.documents().get(documentId=doc_id).execute()
    end_index = doc["body"]["content"][-1]["endIndex"] - 1

    # Formatear tags como hashtags
    tags_line = ""
    if tags and len(tags) > 0:
        tags_line = " ".join("#{}".format(t) for t in tags) + "\n"

    entry_text = "\n[{}]\n{}{}\n".format(hora, tags_line, texto)

    requests = [
        {
            "insertText": {
                "location": {"index": end_index},
                "text": entry_text,
            }
        }
    ]
    docs_service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()

    logger.info("Appended reactivo to doc %s at %s", doc_id, hora)


def save_reactivo(user, fecha, hora, cabecera_data, texto, tags=None):
    """
    Función principal: crea o encuentra el doc del día, agrega el reactivo.

    Args:
        user: User model instance
        fecha: "DD/MM/AAAA"
        hora: "HH:MM"
        cabecera_data: dict con datos Calendaria calculados en JS
        texto: texto del reactivo
        tags: list de strings (palabras clave extraídas del texto)

    Returns:
        dict con doc_url, folder_url
    """
    creds = get_credentials(user)
    if not creds:
        raise ValueError("Google Docs no conectado. Autoriza el acceso primero.")

    docs_service, drive_service = _get_services(creds)

    # Asegurar carpeta
    folder_id = ensure_folder(drive_service)

    # Buscar doc del día
    doc_id = find_doc_for_date(drive_service, folder_id, fecha)

    if not doc_id:
        # Crear doc nuevo con cabecera
        doc_id = create_doc_with_header(
            docs_service, drive_service, folder_id,
            fecha, hora, cabecera_data, user
        )

    # Agregar el reactivo
    append_reactivo(docs_service, doc_id, hora, texto, tags=tags)

    doc_url = "https://docs.google.com/document/d/{}/edit".format(doc_id)
    folder_url = "https://drive.google.com/drive/folders/{}".format(folder_id)
    return {"doc_id": doc_id, "doc_url": doc_url, "folder_url": folder_url}
