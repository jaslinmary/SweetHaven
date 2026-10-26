
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field as PydanticField
from sqlmodel import Session, select

from app.database import get_session
from app.models import Sweet, Order, OrderItem

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


class CartItemInput(BaseModel):
    sweet_id: int
    quantity: int = PydanticField(gt=0, le=100)


class OrderInput(BaseModel):
    customer_name: str = PydanticField(min_length=2, max_length=100)
    phone: str = PydanticField(min_length=10, max_length=20)
    address: str = PydanticField(min_length=5, max_length=500)
    items: list[CartItemInput] = PydanticField(min_length=1)


@router.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    session: Session = Depends(get_session)
):
    sweets = session.exec(
        select(Sweet).where(Sweet.is_active == True)
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"sweets": sweets}
    )


@router.get("/cart", response_class=HTMLResponse)
def cart_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="cart.html",
        context={}
    )


@router.get("/checkout", response_class=HTMLResponse)
def checkout_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context={}
    )


@router.get("/api/products")
def get_products(session: Session = Depends(get_session)):
    return session.exec(
        select(Sweet).where(Sweet.is_active == True)
    ).all()


@router.post("/api/orders", status_code=201)
def create_order(
    data: OrderInput,
    session: Session = Depends(get_session)
):
    try:
        # Validate products and calculate all prices on the server.
        order_lines = []
        total = 0.0

        for item in data.items:
            sweet = session.get(Sweet, item.sweet_id)

            if sweet is None or not sweet.is_active:
                raise HTTPException(
                    status_code=400,
                    detail=f"Sweet {item.sweet_id} is unavailable."
                )

            if sweet.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for {sweet.name}."
                )

            subtotal = round(sweet.price * item.quantity, 2)
            total += subtotal

            order_lines.append({
                "sweet": sweet,
                "quantity": item.quantity,
                "subtotal": subtotal
            })

        order = Order(
            customer_name=data.customer_name.strip(),
            phone=data.phone.strip(),
            address=data.address.strip(),
            total_amount=round(total, 2)
        )

        session.add(order)
        session.flush()

        for line in order_lines:
            sweet = line["sweet"]
            quantity = line["quantity"]

            session.add(
                OrderItem(
                    order_id=order.id,
                    sweet_id=sweet.id,
                    sweet_name=sweet.name,
                    quantity=quantity,
                    unit_price=sweet.price,
                    subtotal=line["subtotal"]
                )
            )

            sweet.stock -= quantity
            session.add(sweet)

        session.commit()
        session.refresh(order)

        return {
            "success": True,
            "message": "Your order has been placed!",
            "order_id": order.id,
            "total": order.total_amount
        }

    except HTTPException:
        session.rollback()
        raise

    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to place your order. Please try again."
        )
