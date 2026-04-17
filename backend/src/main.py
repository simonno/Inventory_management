import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List

from db import Base, engine, get_db, repositories
from . import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bridal Inventory System")

_allow_origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/inventory/", response_model=schemas.DressInventory)
def create_inventory_item(item: schemas.DressInventoryCreate, db: Session = Depends(get_db)):
    return repositories.create_dress(db=db, dress=item)


@app.get("/inventory/", response_model=List[schemas.DressInventory])
def read_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repositories.get_all_dresses(db, skip=skip, limit=limit)


@app.post("/orders/", response_model=schemas.ActiveOrder)
def create_order(order: schemas.ActiveOrderCreate, db: Session = Depends(get_db)):
    try:
        return repositories.create_order(db=db, order=order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/orders/", response_model=List[schemas.ActiveOrder])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repositories.get_all_orders(db, skip=skip, limit=limit)


@app.put("/orders/{order_id}/link/{dress_id}", response_model=schemas.ActiveOrder)
def link_order(order_id: int, dress_id: int, db: Session = Depends(get_db)):
    db_order = repositories.link_order_to_dress(db, order_id=order_id, dress_id=dress_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


_dist = os.path.join(os.getcwd(), "frontend", "dist")
if os.path.isdir(_dist):
    app.mount("/", StaticFiles(directory=_dist, html=True), name="static")
else:
    @app.get("/")
    def read_root():
        return {"status": "ok", "dist": _dist, "exists": os.path.isdir(_dist)}
