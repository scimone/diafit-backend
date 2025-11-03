from ninja import NinjaAPI

from api.router import cgm_router

api = NinjaAPI(
    title="Diafit Backend API",
    version="1.0.0",
    description="API for Diafit Backend",
    urls_namespace="api-swagger",
)

api.add_router("/cgm", cgm_router)
