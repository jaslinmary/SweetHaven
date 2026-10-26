
from datetime import datetime

from sqlmodel import SQLModel, Field


class Sweet(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str
    category: str = Field(index=True)
    price: float
    image_url: str
    stock: int = 100
    is_active: bool = True


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_name: str
    phone: str
    address: str
    total_amount: float
    status: str = "Pending"
    created_at: datetime = Field(default_factory=datetime.now)


class OrderItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", index=True)
    sweet_id: int = Field(foreign_key="sweet.id")
    sweet_name: str
    quantity: int
    unit_price: float
    subtotal: float
