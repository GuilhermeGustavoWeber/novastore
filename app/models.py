"""
Domain models and request/response schemas with strict typing.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class ProductSchema(BaseModel):
    id: int
    name: str
    category: str
    price: float
    description: str
    stock: int
    badge: Optional[str] = None


class OrderItemInput(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantidade deve ser maior que zero")


class CheckoutRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=100)
    customer_email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", description="E-mail valido")
    customer_address: str = Field(min_length=5, max_length=200)
    payment_method: str = Field(pattern="^(pix|cartao|boleto)$")
    items: List[OrderItemInput] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderResponse(BaseModel):
    order_id: str
    customer_name: str
    customer_email: str
    customer_address: str
    payment_method: str
    total_amount: float
    status: str
    created_at: str
    items: List[OrderItemResponse]
