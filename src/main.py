from dotenv import load_dotenv

load_dotenv()

import io
import yaml
import os
import importlib

from fastapi import FastAPI, Response
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from auth import AuthMiddleware

app = FastAPI()

ORIGINS = [
    # TODO: uncomment when we know acceptable GPTEngineer origins
    # "http://localhost:3000",
    # "https://app.backengine.dev",
    # "https://staging.backengine.dev",
    # "https://*.vercel.app",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

API_URL = os.environ.get("API_URL")
BACKENGINE_BASE_URL = os.environ.get("BACKENGINE_BASE_URL")
BACKENGINE_CONTAINER_API_KEY = os.environ.get("BACKENGINE_CONTAINER_API_KEY")
BACKENGINE_PROJECT_ID = os.environ.get("BACKENGINE_PROJECT_ID")
ENV = os.environ.get("ENV")

OPENID_CONFIG_URL = os.environ.get("OPENID_CONFIG_URL")
PROJECT_SHORT_CODE = os.environ.get("PROJECT_SHORT_CODE")
STAGE = os.environ.get("STAGE")


# Function to generate custom OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Interactive API",
        version="0.1.0",
        routes=app.routes,
        servers=[{"url": API_URL}],
    )
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
        }
    }
    openapi_schema["security"] = [{"bearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


@app.get("/docs/json", include_in_schema=False)
async def get_open_api_json():
    return custom_openapi()


# add endpoints
# additional yaml version of openapi.json
@app.get("/docs/yaml", include_in_schema=False)
def read_openapi_yaml() -> Response:
    openapi_json = custom_openapi()
    yaml_s = io.StringIO()
    yaml.dump(openapi_json, yaml_s)
    return Response(yaml_s.getvalue(), media_type="text/yaml")


routes_folder = "api"
for module in os.listdir(routes_folder):
    if module.endswith(".py") and not module.startswith("__"):
        route_module = importlib.import_module(f"{routes_folder}.{module[:-3]}")

        if hasattr(route_module, "router"):
            app.include_router(route_module.router)
