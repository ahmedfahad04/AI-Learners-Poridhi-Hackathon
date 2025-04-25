from fastapi import FastAPI
from routes.routes_products import router as products_router
from routes.routes_config import router as config_router

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

Instrumentator().instrument(app).expose(app)

app.include_router(products_router)
app.include_router(config_router)
