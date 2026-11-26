from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["raw_rows"] == 1050
    assert data["clean_rows"] > 0
    assert data["dropped_rows"] == data["raw_rows"] - data["clean_rows"]


def test_predict_valid_normalization() -> None:
    payload = {"city": "LAHORE", "area_sqft": "1500", "bedrooms": "3", "age_years": "5"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "lahore"
    assert data["predicted_price"] >= 500000
    assert data["city_avg_price_per_sqft"] > 0
    assert data["model_version"] == "v1.0-baseline"


def test_predict_invalid_city() -> None:
    payload = {"city": "karachi", "area_sqft": 1500, "bedrooms": 3, "age_years": 5}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_invalid_area() -> None:
    payload = {"city": "lahore", "area_sqft": -100, "bedrooms": 3, "age_years": "5"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_cities_endpoint() -> None:
    response = client.get("/cities")
    assert response.status_code == 200
    data = response.json()
    assert data["supported_cities"] == ["faisalabad", "lahore", "islamabad"]
    assert data["total_cities"] == 3
