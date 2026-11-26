import logging

from fastapi import FastAPI, HTTPException

from app.predictor import load_and_clean_data, predict_price
from app.schema import (
    CitiesResponse,
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
    StatsResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ML House Price Serving API", version="1.0.0")


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    _, raw_rows, clean_rows = load_and_clean_data()
    dropped_rows = raw_rows - clean_rows
    return HealthResponse(
        status="healthy",
        raw_rows=raw_rows,
        clean_rows=clean_rows,
        dropped_rows=dropped_rows,
    )


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    logger.info("Prediction request received for city=%s", request.city)
    try:
        predicted, avg_ppsqft = predict_price(
            request.city,
            request.area_sqft,
            request.bedrooms,
            request.age_years,
        )
    except Exception as exc:
        logger.exception("Prediction calculation failed")
        raise HTTPException(status_code=500, detail="Prediction failed") from exc

    return PredictionResponse(
        city=request.city,
        predicted_price=predicted,
        city_avg_price_per_sqft=avg_ppsqft,
        model_version="v1.0-baseline",
    )


@app.get("/cities", response_model=CitiesResponse)
def list_cities() -> CitiesResponse:
    cities = ["faisalabad", "lahore", "islamabad"]
    return CitiesResponse(supported_cities=cities, total_cities=len(cities))
