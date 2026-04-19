import logging
import jwt
from flask import Blueprint, request, jsonify
from logic import generate_pdf_a3, extract_xml_from_pdf, extract_all_attachments

logger = logging.getLogger("PDF-a3")
pdf_bp = Blueprint("pdf_a3", __name__, url_prefix="/pdf-a3")


def validate_token(auth_header):
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, 401, "Missing or malformed Authorization header"
    token = auth_header.split(" ", 1)[1]
    if not token:
        return None, 403, "Token validation failed"
    return "test-user", None, None


@pdf_bp.route("/generate", methods=["POST"])
def generate():
    """
    Generate a PDF/A-3 document by embedding XML and attachments.
    ---
    tags:
      - PDF/A-3
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [pdf, xml]
          properties:
            pdf:
              type: object
              properties:
                content:
                  type: string
            xml:
              type: object
              properties:
                content:
                  type: string
            lang:
              type: string
              example: en-US
            afrelationship:
              type: string
              example: data
            attachments:
              type: array
              items:
                type: object
    responses:
      200:
        description: PDF/A-3 generated successfully
      400:
        description: Bad request
      401:
        description: Unauthorized - missing token
      403:
        description: Forbidden - token validation failed
    """
    sub, code, err = validate_token(request.headers.get("Authorization"))
    if not sub:
        return jsonify({"successful": False, "error": err}), code

    data = request.get_json()
    if not data:
        return jsonify({"successful": False, "error": "Request body must be JSON"}), 400

    pdf_content = data.get("pdf", {}).get("content")
    xml_content = data.get("xml", {}).get("content")

    if not pdf_content or not xml_content:
        return jsonify({"successful": False, "error": "Both 'pdf.content' and 'xml.content' are required"}), 400

    try:
        result = generate_pdf_a3(
            pdf_content,
            xml_content,
            lang=data.get("lang"),
            afrelationship=data.get("afrelationship"),
            attachments=data.get("attachments"),
        )
        logger.info(f"PDF/A-3 generated for user {sub}")
        return jsonify({"successful": True, "pdfa3": {"content": result}})
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({"successful": False, "error": str(e)}), 400


@pdf_bp.route("/extract", methods=["POST"])
def extract():
    """
    Extract all attachments and XML from a PDF/A-3 document.
    ---
    tags:
      - PDF/A-3
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [pdfa3]
          properties:
            pdfa3:
              type: object
              properties:
                content:
                  type: string
    responses:
      200:
        description: Attachments extracted successfully
      400:
        description: Bad request
      401:
        description: Unauthorized - missing token
      403:
        description: Forbidden - token validation failed
    """
    sub, code, err = validate_token(request.headers.get("Authorization"))
    if not sub:
        return jsonify({"successful": False, "error": err}), code

    data = request.get_json()
    if not data:
        return jsonify({"successful": False, "error": "Request body must be JSON"}), 400

    pdf_content = data.get("pdfa3", {}).get("content")
    if not pdf_content:
        return jsonify({"successful": False, "error": "'pdfa3.content' is required"}), 400

    try:
        xml_info = extract_xml_from_pdf(pdf_content)
        attachments = extract_all_attachments(pdf_content)
        logger.info(f"Extraction done for user {sub}")
        return jsonify({
            "successful": True,
            "attachments": attachments,
            "xml": xml_info,
        })
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return jsonify({"successful": False, "error": str(e)}), 400
