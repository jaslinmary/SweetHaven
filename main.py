
from contextlib import asynccontextmanager
from pathlib import Path

import os
from starlette.middleware.sessions import SessionMiddleware

from fastapi.exception_handlers import http_exception_handler
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from sqlalchemy import func

from app.models.user import User
from app.security import hash_password, verify_password


from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem

from app.database import engine, create_db_and_tables
from app.models.user import User




BASE_DIR = Path(__file__).resolve().parent
APP_DIR = BASE_DIR / "app"


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Sweet Haven | Kerala Sweets",
    lifespan=lifespan
)



@app.exception_handler(HTTPException)
async def custom_http_exception_handler(
    request: Request,
    exc: HTTPException
):
    if request.url.path.startswith("/admin"):
        if exc.status_code == 401:
            return RedirectResponse(
                url="/login",
                status_code=303
            )

        if exc.status_code == 403:
            return HTMLResponse(
                content="""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport"
                          content="width=device-width, initial-scale=1.0">
                    <title>Access Denied | SweetHaven</title>
                </head>
                <body style="font-family: Arial, sans-serif;
                             background: #fffaf3;
                             color: #102c20;
                             text-align: center;
                             padding: 80px 20px;">
                    <h1>Access Denied</h1>
                    <p>You don't have permission to access this admin page.</p>
                    <a href="/" style="color: #102c20;">
                        Return to Home
                    </a>
                </body>
                </html>
                """,
                status_code=403
            )

    return await http_exception_handler(request, exc)



app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get(
        "SWEETHAVEN_SECRET_KEY",
        "dev-only-change-this-secret-key"
    ),
    same_site="lax",
    https_only=False
)


app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
def require_admin(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Please log in to access admin pages."
        )

    with Session(engine) as session:
        user = session.get(User, user_id)

        if not user or not user.is_active:
            request.session.clear()
            raise HTTPException(
                status_code=401,
                detail="Please log in again."
            )

        if user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Admin access required."
            )


# ==============================
# ADMIN ROUTE PROTECTION
# ==============================

# ==============================
# ADMIN ROUTE PROTECTION
# ==============================


# ==============================
# CUSTOMER REGISTRATION
# ==============================

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"error": None}
    )


@app.post("/register", response_class=HTMLResponse)
def register_customer(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    name = name.strip()
    email = email.strip().lower()

    if not name or len(password) < 8:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": "Enter your name and a password of at least 8 characters."
            },
            status_code=400
        )

    with Session(engine) as session:
        existing_user = session.exec(
            select(User).where(User.email == email)
        ).first()

        if existing_user:
            return templates.TemplateResponse(
                request=request,
                name="register.html",
                context={"error": "This email is already registered."},
                status_code=400
            )

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="customer"
        )

        session.add(user)
        session.commit()

    return RedirectResponse(url="/login", status_code=303)


# ==============================
# LOGIN
# ==============================

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": None}
    )


@app.post("/login", response_class=HTMLResponse)
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    email = email.strip().lower()

    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.email == email)
        ).first()

        if (
            not user
            or not user.is_active
            or not verify_password(password, user.password_hash)
        ):
            return templates.TemplateResponse(
                request=request,
                name="login.html",
                context={"error": "Invalid email or password."},
                status_code=401
            )

        user_id = user.id
        user_role = user.role

    request.session.clear()
    request.session["user_id"] = user_id
    request.session["role"] = user_role

    if user_role == "admin":
        return RedirectResponse(
            url="/admin/dashboard",
            status_code=303
        )

    return RedirectResponse(url="/", status_code=303)





@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)



@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    with Session(engine) as session:
        products = session.exec(
            select(Product)
        ).all()

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"products": products}
    )

@app.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="cart.html",
        context={}
    )


@app.get("/checkout", response_class=HTMLResponse)
async def checkout_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context={}
    )

@app.post("/place-order")
async def place_order(
    customer_name: str = Form(...),
    customer_phone: str = Form(...),
    customer_email: str = Form(""),
    delivery_address: str = Form(...),
    customer_district: str = Form(...),
    customer_pincode: str = Form(...),
    payment_method: str = Form("COD"),
    order_notes: str = Form(""),
    cart_items: str = Form(...)
):
    import json

    try:
        items = json.loads(cart_items)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid cart data."
        )

    if not isinstance(items, list) or not items:
        raise HTTPException(
            status_code=400,
            detail="Your cart is empty."
        )
    
    # Combine duplicate products into one quantity
    combined_items = {}

    for item in items:
        try:
            product_id = int(item["id"])
            quantity = int(item["quantity"])
        except (KeyError, TypeError, ValueError):
            raise HTTPException(
                status_code=400,
                detail="Invalid product or quantity."
            )

        if quantity < 1:
            raise HTTPException(
                status_code=400,
                detail="Quantity must be at least one."
            )

        combined_items[product_id] = (
            combined_items.get(product_id, 0) + quantity
        )

    items = [
        {"id": product_id, "quantity": quantity}
        for product_id, quantity in combined_items.items()
    ]


    if payment_method not in ("COD", "ONLINE"):
        raise HTTPException(
            status_code=400,
            detail="Invalid payment method."
        )

    with Session(engine) as session:
        order = Order(
            customer_name=customer_name.strip(),
            customer_phone=customer_phone.strip(),
            customer_email=customer_email.strip() or None,
            delivery_address=delivery_address.strip(),
            customer_district=customer_district.strip(),
            customer_pincode=customer_pincode.strip(),
            total_amount=0,
            payment_method=payment_method,
            order_status="Pending",
            order_notes=order_notes.strip() or None
        )

        session.add(order)
        session.flush()

        total = 0.0
        order_items = []

        for item in items:
            try:
                product_id = int(item["id"])
                quantity = int(item["quantity"])
            except (KeyError, TypeError, ValueError):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid product or quantity."
                )

            if quantity < 1:
                raise HTTPException(
                    status_code=400,
                    detail="Quantity must be at least one."
                )

            product = session.get(Product, product_id)

            if not product or not product.is_available:
                raise HTTPException(
                    status_code=400,
                    detail="A selected product is unavailable."
                )

           
                        
            if quantity > product.stock:
                session.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Only {product.stock} units of {product.name} are available."
                )


            subtotal = round(product.price * quantity, 2)
            total += subtotal

            order_items.append(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    quantity=quantity,
                    unit_price=product.price,
                    subtotal=subtotal
                )
            )

        order.total_amount = round(total, 2)

        for order_item in order_items:
            session.add(order_item)

        for item in items:
            product = session.get(Product, int(item["id"]))
            product.stock -= int(item["quantity"])

            if product.stock <= 0:
                product.is_available = False

        
        session.add(order)

        try:
            session.commit()
            session.refresh(order)
            order_id = order.id

        except Exception:
            session.rollback()
            raise HTTPException(
                status_code=500,
                detail="Unable to place your order. Please try again."
            )


    return RedirectResponse(
        url=f"/order-success/{order_id}",
        status_code=303
    )


@app.get("/order-success/{order_id}", response_class=HTMLResponse)
async def order_success(request: Request, order_id: int):
    with Session(engine) as session:
        order = session.get(Order, order_id)

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found."
            )

        items = session.exec(
            select(OrderItem).where(
                OrderItem.order_id == order_id
            )
        ).all()

    return templates.TemplateResponse(
        request=request,
        name="order_success.html",
        context={
            "order": order,
            "items": items
        }
    )



@app.get(
    "/admin/orders",
    dependencies=[Depends(require_admin)]
)
async def admin_orders(request: Request):
    with Session(engine) as session:
        statement = select(Order).order_by(Order.id.desc())
        orders = session.exec(statement).all()

    return templates.TemplateResponse(
        request=request,
        name="admin_orders.html",
        context={"orders": orders}
    )



@app.post(
    "/admin/orders/{order_id}/status",
    dependencies=[Depends(require_admin)]
)
async def update_order_status(
    order_id: int,
    status: str = Form(...)
):
    allowed_statuses = [
        "Pending",
        "Confirmed",
        "Processing",
        "Shipped",
        "Delivered",
        "Cancelled"
    ]

    print(f"DEBUG: Order ID = {order_id}")
    print(f"DEBUG: Received status = {status}")

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status"
        )

    with Session(engine) as session:
        order = session.get(Order, order_id)

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        print(f"DEBUG: Old status = {order.order_status}")

        order.order_status = status
        session.add(order)
        session.commit()
        session.refresh(order)

        print(f"DEBUG: Saved status = {order.order_status}")

    return RedirectResponse(
        url="/admin/orders",
        status_code=303
    )



@app.get(
    "/admin/orders/{order_id}",
    dependencies=[Depends(require_admin)]
)

async def order_details(request: Request, order_id: int):
    with Session(engine) as session:
        order = session.get(Order, order_id)

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

    return templates.TemplateResponse(
        request=request,
        name="order_details.html",
        context={"order": order}
    )

@app.get(
    "/admin/dashboard",
    dependencies=[Depends(require_admin)]
)
async def admin_dashboard(request: Request):

    with Session(engine) as session:

        # Total number of orders
        total_orders = session.exec(
            select(func.count(Order.id))
        ).one()

        # Total sales excluding cancelled orders
        total_sales = session.exec(
            select(func.coalesce(func.sum(Order.total_amount), 0))
            .where(Order.order_status != "Cancelled")
        ).one()

        # Pending orders
        pending_orders = session.exec(
            select(func.count(Order.id))
            .where(Order.order_status == "Pending")
        ).one()

        # Delivered orders
        delivered_orders = session.exec(
            select(func.count(Order.id))
            .where(Order.order_status == "Delivered")
        ).one()

        # Five most recent orders
        recent_orders = session.exec(
            select(Order)
            .order_by(Order.id.desc())
            .limit(5)
        ).all()

    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "total_orders": total_orders,
            "total_sales": total_sales,
            "pending_orders": pending_orders,
            "delivered_orders": delivered_orders,
            "recent_orders": recent_orders,
        }
    )



@app.get(
    "/admin/products",
    dependencies=[Depends(require_admin)]
)
async def admin_products(request: Request):
    with Session(engine) as session:
        products = session.exec(
            select(Product).order_by(Product.id.desc())
        ).all()

    return templates.TemplateResponse(
        request=request,
        name="admin_products.html",
        context={"products": products}
    )



@app.post(
    "/admin/products/add",
    dependencies=[Depends(require_admin)]
)
async def add_product(
    name: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    stock: int = Form(0),
    image: str = Form(""),
    description: str = Form(...)
):
    if not name.strip():
        raise HTTPException(status_code=400, detail="Sweet name is required.")

    if price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than zero.")

    if stock < 0:
        raise HTTPException(status_code=400, detail="Stock cannot be negative.")

    if not image.strip():
        raise HTTPException(status_code=400, detail="Please provide an image URL or path.")

    product = Product(
        name=name.strip(),
        category=category.strip(),
        price=price,
        stock=stock,
        image=image.strip(),
        description=description.strip(),
        is_available=stock > 0
    )

    with Session(engine) as session:
        session.add(product)
        session.commit()

    return RedirectResponse(
        url="/admin/products",
        status_code=303
    )



@app.post(
    "/admin/products/{product_id}/edit",
    dependencies=[Depends(require_admin)]
)
async def edit_product(
    product_id: int,
    name: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    image: str = Form(...),
    description: str = Form(...)
):
    with Session(engine) as session:
        product = session.get(Product, product_id)

        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        if price <= 0 or stock < 0:
            raise HTTPException(
                status_code=400,
                detail="Price must be positive and stock cannot be negative."
            )

        if not name.strip() or not image.strip():
            raise HTTPException(
                status_code=400,
                detail="Product name and image are required."
            )

        product.name = name.strip()
        product.category = category.strip()
        product.price = price
        product.stock = stock
        product.image = image.strip()
        product.description = description.strip()
        product.is_available = stock > 0

        session.add(product)
        session.commit()

    return RedirectResponse(url="/admin/products", status_code=303)


@app.post(
    "/admin/products/{product_id}/delete",
    dependencies=[Depends(require_admin)]
)

async def delete_product(product_id: int):
    with Session(engine) as session:
        product = session.get(Product, product_id)

        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        session.delete(product)
        session.commit()

    return RedirectResponse(url="/admin/products", status_code=303)



@app.get(
    "/admin/products/{product_id}/edit",
    dependencies=[Depends(require_admin)]
)
async def edit_product_page(request: Request, product_id: int):
    with Session(engine) as session:
        product = session.get(Product, product_id)

        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        product_data = {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "stock": product.stock,
            "image": product.image,
            "description": product.description,
        }

    return templates.TemplateResponse(
        request=request,
        name="edit_product.html",
        context={"product": product_data}
    )



@app.get("/track-order")
async def track_order_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="track_order.html",
        context={
            "order": None,
            "error": None
        }
    )


@app.post("/track-order")
async def track_customer_order(
    request: Request,
    order_id: int = Form(...),
    customer_phone: str = Form(...)
):
    with Session(engine) as session:
        order = session.get(Order, order_id)

        # Verify both order ID and phone number
        if (
            order is None
            or order.customer_phone.strip() != customer_phone.strip()
        ):
            return templates.TemplateResponse(
                request=request,
                name="track_order.html",
                context={
                    "order": None,
                    "error": "No order found with those details. Please check your order ID and phone number."
                }
            )

        return templates.TemplateResponse(
            request=request,
            name="track_order.html",
            context={
                "order": order,
                "error": None
            }
        )


@app.get("/stock-error", response_class=HTMLResponse)
async def stock_error(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="stock_error.html",
        context={
            "message": "Your selected quantity exceeds the available stock. Please return to checkout and reduce the quantity."
        }
    )



@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        request=request,
        name="404.html",
        context={},
        status_code=404
    )


