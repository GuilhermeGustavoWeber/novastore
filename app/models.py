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
    specs: Optional[str] = None
    image_url: Optional[str] = None
    avg_rating: float = 0.0
    review_count: int = 0


class ProductCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    category: str = Field(min_length=2, max_length=60)
    price: float = Field(gt=0)
    description: str = Field(min_length=5, max_length=500)
    stock: int = Field(ge=0)
    badge: Optional[str] = None
    specs: Optional[str] = None
    image_url: Optional[str] = None


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    category: Optional[str] = Field(default=None, min_length=2, max_length=60)
    price: Optional[float] = Field(default=None, gt=0)
    description: Optional[str] = Field(default=None, min_length=5, max_length=500)
    stock: Optional[int] = Field(default=None, ge=0)
    badge: Optional[str] = None
    specs: Optional[str] = None
    image_url: Optional[str] = None


class ReviewSchema(BaseModel):
    id: int
    product_id: int
    author_name: str
    rating: int
    comment: str
    created_at: str


class ReviewCreateRequest(BaseModel):
    author_name: str = Field(min_length=2, max_length=80)
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=3, max_length=400)


class CouponSchema(BaseModel):
    code: str
    discount_percent: float = Field(ge=0, le=100)
    free_shipping: bool = False
    active: bool = True


class CouponValidateRequest(BaseModel):
    code: str = Field(min_length=2, max_length=30)
    subtotal: float = Field(ge=0)


class CouponValidateResponse(BaseModel):
    valid: bool
    code: str
    discount_percent: float
    discount_amount: float
    free_shipping: bool
    message: str


class ShippingQuoteRequest(BaseModel):
    zip_code: str = Field(min_length=8, max_length=10)
    subtotal: float = Field(ge=0)
    coupon_code: Optional[str] = None


class ShippingQuoteResponse(BaseModel):
    zip_code: str
    region: str
    cost: float
    estimated_days: int
    free_shipping_applied: bool


class OrderItemInput(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantidade deve ser maior que zero")


class CheckoutRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=100)
    customer_email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", description="E-mail valido")
    customer_address: str = Field(min_length=5, max_length=200)
    zip_code: Optional[str] = Field(default="80000-000", min_length=8, max_length=10)
    payment_method: str = Field(pattern="^(pix|cartao|boleto)$")
    coupon_code: Optional[str] = None
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
    zip_code: str = "80000-000"
    payment_method: str
    subtotal_amount: float = 0.0
    discount_amount: float = 0.0
    shipping_cost: float = 0.0
    coupon_code: Optional[str] = None
    total_amount: float
    status: str
    created_at: str
    items: List[OrderItemResponse]


class OrderStatusUpdateRequest(BaseModel):
    status: str = Field(pattern="^(Confirmado|Em Separacao|Enviado|Entregue|Cancelado)$")


class AdminMetricsResponse(BaseModel):
    total_revenue: float
    total_orders: int
    average_ticket: float
    active_products: int
    low_stock_count: int
    orders_by_status: dict[str, int]
