
from pathlib import Path

from sqlmodel import SQLModel, Session, create_engine

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_FILE = BASE_DIR / "sweethaven.db"

DATABASE_URL = f"sqlite:///{DATABASE_FILE.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)


def create_db_and_tables():
    # Import models before creating tables.
    from app.models import Sweet, Order, OrderItem

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
