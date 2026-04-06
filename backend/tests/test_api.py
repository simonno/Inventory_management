import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta

from backend.src.main import app
from backend.src.database import Base, get_db

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_inventory_item():
    response = client.post(
        "/inventory/",
        json={
            "model_number": "B-2024",
            "size": "38",
            "cup_size": "B",
            "is_custom_sewing": False,
            "storage_location": "Tel Aviv",
            "dress_condition": "Good",
            "status": "In Stock",
            "notes": "Classic white"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["model_number"] == "B-2024"
    assert data["item_id"] == 1

def test_create_order_validation():
    # Wedding date before measurement date (should fail)
    response = client.post(
        "/orders/",
        json={
            "model_number": "B-2024",
            "bride_name": "Test Bride",
            "first_measurement_date": str(date.today()),
            "wedding_date": str(date.today() - timedelta(days=1)),
            "size": "38",
            "bust_cm": 90,
            "hips_cm": 95,
            "waist_cm": 70,
            "cup_size": "B",
            "height_cm": 170,
            "is_custom_sewing": False,
            "order_type": "New Order"
        },
    )
    assert response.status_code == 422
    # FastAPI returns list of errors in 'detail' for validation errors
    errors = response.json()["detail"]
    assert any("Wedding date must be after first measurement date" in error["msg"] for error in errors)

def test_link_order_to_dress():
    # Create dress
    client.post(
        "/inventory/",
        json={
            "model_number": "B-2024",
            "size": "38",
            "cup_size": "B",
            "is_custom_sewing": False,
            "storage_location": "Tel Aviv",
            "dress_condition": "Good",
            "status": "In Stock"
        },
    )
    
    # Create order
    client.post(
        "/orders/",
        json={
            "model_number": "B-2024",
            "bride_name": "Test Bride",
            "first_measurement_date": str(date.today()),
            "wedding_date": str(date.today() + timedelta(days=30)),
            "size": "38",
            "bust_cm": 90,
            "hips_cm": 95,
            "waist_cm": 70,
            "cup_size": "B",
            "height_cm": 170,
            "is_custom_sewing": False,
            "order_type": "New Order"
        },
    )
    
    # Link
    response = client.put("/orders/1/link/1")
    assert response.status_code == 200
    data = response.json()
    assert data["dress_id"] == 1
