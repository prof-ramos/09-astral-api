"""
OpenAPI schema generation script for Astrologer API
"""

from app.main import app
import json

def dump_schema(output_file_path: str):
    """Gera o openapi.json a partir da instância do FastAPI."""
    openapi_data = app.openapi()
    with open(output_file_path, 'w') as file:
        json.dump(openapi_data, file, indent=2)

if __name__ == "__main__":
    dump_schema("openapi.json")
    print("OpenAPI JSON file generated successfully!")
    print("You can view it at: https://editor-next.swagger.io/")