from typing import Optional

from sqlmodel import SQLModel, Field


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str
    category: str = Field(index=True)
    price: float
    image: str
    stock: int = Field(default=0)
    is_available: bool = Field(default=True)