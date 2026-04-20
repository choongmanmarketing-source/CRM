"""Vercel entrypoint for Restaurant CRM web API."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from crm import RestaurantCRM  # noqa: E402

app = FastAPI(title="Restaurant CRM API", version="1.0.0")


class CreateCustomerRequest(BaseModel):
    name: str = Field(min_length=1)
    phone: str = Field(min_length=6)


class PurchaseRequest(BaseModel):
    phone: str = Field(min_length=6)
    amount: float = Field(ge=0)
    earn_rate: int = Field(default=10, gt=0)
    use_points: int = Field(default=0, ge=0)
    note: str | None = None


def get_crm() -> RestaurantCRM:
    return RestaurantCRM()


@app.get("/")
def home() -> dict[str, object]:
    return {
        "message": "Restaurant CRM API is running on Vercel",
        "docs": "/docs",
        "endpoints": [
            "POST /customers",
            "GET /customers",
            "GET /customers/{phone}",
            "POST /purchase",
        ],
    }


@app.post("/customers")
def create_customer(payload: CreateCustomerRequest) -> dict[str, object]:
    crm = get_crm()
    try:
        customer = crm.add_customer(payload.name, payload.phone)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "id": customer.id,
        "name": customer.name,
        "phone": customer.phone,
        "points": customer.points,
        "tier": customer.tier,
    }


@app.get("/customers")
def customers() -> list[dict[str, object]]:
    crm = get_crm()
    return [
        {
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
            "points": c.points,
            "tier": c.tier,
        }
        for c in crm.list_customers()
    ]


@app.get("/customers/{phone}")
def customer_profile(phone: str) -> dict[str, object]:
    crm = get_crm()
    customer = crm.get_customer_by_phone(phone)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {
        "id": customer.id,
        "name": customer.name,
        "phone": customer.phone,
        "points": customer.points,
        "tier": customer.tier,
    }


@app.post("/purchase")
def purchase(payload: PurchaseRequest) -> dict[str, object]:
    crm = get_crm()
    try:
        customer = crm.record_purchase(
            phone=payload.phone,
            amount=payload.amount,
            earn_rate=payload.earn_rate,
            use_points=payload.use_points,
            note=payload.note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "id": customer.id,
        "name": customer.name,
        "phone": customer.phone,
        "points": customer.points,
        "tier": customer.tier,
    }
