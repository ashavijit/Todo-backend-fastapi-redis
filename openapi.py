import os
from loguru import logger
from fastapi.openapi.utils import get_openapi

ROOT_URL=os.getenv('ROOT_URL')

def init_openAPI(app):
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="FastAPI",
            version="0.0.1",
            description="This is a Todo API that allows you to create, read, update and delete todos.(avijitjsx.codes)",
            routes=app.routes,
        )
        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    app.openapi = custom_openapi
    return app