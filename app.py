import logging
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from routes import pdf_bp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PDF-a3")

app = Flask(__name__)
CORS(app)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/pdf-a3/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/pdf-a3/apidocs/",
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "PDF/A-3 API",
        "description": "API for generating and extracting PDF/A-3 documents",
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter: Bearer <your_token>",
        }
    },
    "security": [{"Bearer": []}],
}

Swagger(app, config=swagger_config, template=swagger_template)
app.register_blueprint(pdf_bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
