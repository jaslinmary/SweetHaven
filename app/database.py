from sqlmodel import SQLModel, Session, create_engine

# SQLite database file will be created in the project root
DATABASE_URL = "sqlite:///./sweethaven.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)




def create_db_and_tables():
    # Register all models before creating tables
    from app.models.product import Product
    from app.models.order import Order
    from app.models.order_item import OrderItem
    from app.models.user import User

    SQLModel.metadata.create_all(engine)




def get_session():
    with Session(engine) as session:
        yield session