
from getpass import getpass

from sqlmodel import Session, select

from app.database import engine, create_db_and_tables
from app.models.user import User
from app.security import hash_password


def create_admin():
    create_db_and_tables()

    print("\n=== SweetHaven Admin Account Setup ===")

    name = input("Enter admin name: ").strip()
    email = input("Enter admin email: ").strip().lower()
    password = getpass("Create admin password (minimum 8 characters): ")
    confirm_password = getpass("Confirm admin password: ")

    if not name or not email:
        print("Error: Name and email are required.")
        return

    if len(password) < 8:
        print("Error: Password must contain at least 8 characters.")
        return

    if password != confirm_password:
        print("Error: Passwords do not match.")
        return

    with Session(engine) as session:
        existing_user = session.exec(
            select(User).where(User.email == email)
        ).first()

        if existing_user:
            print("Error: This email already has an account.")
            print("Choose a different email for the admin account.")
            return

        admin = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="admin",
            is_active=True
        )

        session.add(admin)
        session.commit()

    print("\nAdmin account created successfully!")
    print("You can now log in using your admin email and password.")


if __name__ == "__main__":
    create_admin()
