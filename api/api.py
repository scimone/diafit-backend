from ninja import NinjaAPI

from api.router import (
    bolus_router,
    cgm_router,
    heart_rate_router,
    meal_router,
    sleep_router,
    summary_router,
)

api = NinjaAPI(
    title="Diafit Backend API",
    version="1.0.0",
    description="API for Diafit Backend",
    urls_namespace="api-swagger",
)

api.add_router("/cgm", cgm_router)
api.add_router("/bolus", bolus_router)
api.add_router("/meal", meal_router)
api.add_router("/summary", summary_router)
api.add_router("/sleep", sleep_router)
api.add_router("/heart_rate", heart_rate_router)
