
from typing import Optional
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)

    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None

    delivery_address: str
    customer_district: str
    customer_pincode: str

    total_amount: float
    payment_method: str = "COD"
    order_status: str = "Pending"
    order_notes: Optional[str] = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
