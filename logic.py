import base64
import io
from facturx import generate_from_binary, get_xml_from_pdf


def generate_pdf_a3(pdf_base64, xml_base64, lang=None, afrelationship=None, attachments=None):
    pdf_bytes = base64.b64decode(pdf_base64)
    xml_bytes = base64.b64decode(xml_base64)

    result_pdf = generate_from_binary(
        pdf_bytes,
        xml_bytes,
        lang=lang or "en-US",
        afrelationship=afrelationship or "data",
        attachments=_prepare_attachments(attachments),
        check_xsd=False,
        check_schematron=False,
    )

    return base64.b64encode(result_pdf).decode("utf-8")


def extract_xml_from_pdf(pdf_base64):
    pdf_bytes = base64.b64decode(pdf_base64)
    pdf_file = io.BytesIO(pdf_bytes)

    xml_filename, xml_bytes = get_xml_from_pdf(pdf_file)
    return {
        "content": base64.b64encode(xml_bytes).decode("utf-8"),
        "mimeType": "application/xml",
        "filename": xml_filename or "metadata.xml",
    }


def extract_all_attachments(pdf_base64):
    from pypdf import PdfReader

    pdf_bytes = base64.b64decode(pdf_base64)
    pdf_file = io.BytesIO(pdf_bytes)

    reader = PdfReader(pdf_file)
    attachments = []

    for name, content_list in reader.attachments.items():
        for content in content_list:
            attachments.append({
                "content": base64.b64encode(content).decode("utf-8"),
                "mimeType": _guess_mime(name),
                "filename": name,
            })

    return attachments


def _prepare_attachments(attachments):
    if not attachments:
        return {}
    result = {}
    for att in attachments:
        filename = att.get("filename", "attachment.bin")
        content = base64.b64decode(att["content"])
        result[filename] = {
            "filedata": content,
            "description": filename,
            "mime": att.get("mimeType", "application/octet-stream"),
        }
    return result


def _guess_mime(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    mime_map = {
        "xml": "application/xml",
        "pdf": "application/pdf",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "txt": "text/plain",
        "json": "application/json",
    }
    return mime_map.get(ext, "application/octet-stream")
