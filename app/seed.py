from sqlmodel import Session, select

from app.database import engine, create_db_and_tables
from app.models.product import Product


products = [
    Product(
        name="Unniyappam",
        description="Traditional Kerala sweet made with banana, rice and jaggery.",
        category="Unniyappam",
        price=80,
        image="/static/images/unniyappam.jpg",
        stock=30
    ),
    Product(
        name="Mysore Pak",
        description="Rich and delicious traditional ghee sweet.",
        category="Mysore Pak",
        price=120,
        image="/static/images/mysore-pak.jpg",
        stock=25
    ),
    Product(
        name="Banana Halwa",
        description="Soft Kerala banana halwa prepared with traditional flavours.",
        category="Halwa",
        price=150,
        image="/static/images/banana-halwa.jpg",
        stock=20
    ),
    Product(
        name="Laddu",
        description="Delicious golden laddus for every celebration.",
        category="Laddu",
        price=100,
        image="/static/images/laddu.jpg",
        stock=25
    ),
    Product(
        name="Palada Payasam",
        description="Creamy traditional Kerala payasam.",
        category="Payasam",
        price=180,
        image="/static/images/palada-payasam.jpg",
        stock=15
    ),
]


def seed_products():
    create_db_and_tables()

    with Session(engine) as session:
        for product in products:
            existing = session.exec(
                select(Product).where(Product.name == product.name)
            ).first()

            if existing is None:
                session.add(product)

        session.commit()

    print("Kerala sweets added successfully!")


if __name__ == "__main__":
    seed_products()
