import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername="mysql+pymysql",
        username=os.environ.get("DB_USER", "admin"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get(
            "DB_HOST",
            "myappdb.c34ucoyis41w.ap-south-1.rds.amazonaws.com"
        ),
        port=3306,
        database=os.environ.get("DB_NAME", "second_project_db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
