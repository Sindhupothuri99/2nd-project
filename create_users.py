from app import app, db, User
from werkzeug.security import generate_password_hash
from getpass import getpass

accounts = [
    ("admin@eduprime.com", "admin"),
    ("faculty@eduprime.com", "faculty"),
    ("student@eduprime.com", "student")
]

with app.app_context():

    for email, role in accounts:

        print(f"\nCreate password for {email}")
        password = getpass("Enter password: ")

        if len(password) < 8:
            print("Password must contain at least 8 characters.")
            continue

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            print(f"Account already exists: {email}")
            continue

        user = User(
            email=email,
            password=generate_password_hash(password),
            role=role
        )

        db.session.add(user)
        db.session.commit()

        print(f"{role.capitalize()} account created successfully!")

print("\nAccount creation process completed.")
