from ninja import NinjaAPI

from api.router import bolus_router, cgm_router, meal_router

api = NinjaAPI(
    title="Diafit Backend API",
    version="1.0.0",
    description="API for Diafit Backend",
    urls_namespace="api-swagger",
)

api.add_router("/cgm", cgm_router)
api.add_router("/bolus", bolus_router)
api.add_router("/meal", meal_router)
