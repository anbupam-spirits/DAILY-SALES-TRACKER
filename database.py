from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Date,
    Time,
    Text,
    DateTime
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# -------------------------------------------------------------------
# Database Configuration
# -------------------------------------------------------------------

DB_PATH = os.path.join(os.path.expanduser("~"), "field_sales.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

Base = declarative_base()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -------------------------------------------------------------------
# Models
# -------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="SR")  # SR / ADMIN
    full_name = Column(String, nullable=True)


class StoreVisit(Base):
    __tablename__ = "store_visits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    visit_date = Column(Date, nullable=False)
    visit_time = Column(Time, nullable=False)
    sr_name = Column(String, nullable=False)
    username = Column(String, nullable=True)
    store_name = Column(String, nullable=False)
    visit_type = Column(String, nullable=False)
    store_category = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    lead_type = Column(String, nullable=False)
    follow_up_date = Column(String, nullable=True)
    products = Column(String, nullable=False)
    order_details = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    maps_url = Column(String, nullable=True)
    location_recorded_answer = Column(String, nullable=False)
    image_data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

# -------------------------------------------------------------------
# Core DB Functions
# -------------------------------------------------------------------

def init_db():
    """Create tables and seed default users."""
    Base.metadata.create_all(bind=engine)
    create_initial_users()


def save_visit(data: dict):
    """Save a store visit."""
    session = SessionLocal()
    try:
        visit = StoreVisit(
            visit_date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
            visit_time=datetime.strptime(data["time"], "%H:%M:%S").time(),
            sr_name=data["sr_name"],
            username=data.get("username"),
            store_name=data["store_name"],
            visit_type=data["visit_type"],
            store_category=data["store_category"],
            phone_number=data["phone"],
            lead_type=data["lead_type"],
            follow_up_date=data.get("follow_up_date"),
            products=data["products"],
            order_details=data.get("order_details"),
            latitude=float(data["latitude"]) if data.get("latitude") else None,
            longitude=float(data["longitude"]) if data.get("longitude") else None,
            maps_url=data.get("maps_url"),
            location_recorded_answer=data["location_recorded_answer"],
            image_data=data["image_data"]
        )

        session.add(visit)
        session.commit()
        session.refresh(visit)
        return True, f"Saved with ID: {visit.id}"

    except Exception as e:
        session.rollback()
        return False, str(e)

    finally:
        session.close()


def get_all_visits():
    session = SessionLocal()
    try:
        return session.query(StoreVisit).order_by(
            StoreVisit.visit_date.desc(),
            StoreVisit.visit_time.desc()
        ).all()
    finally:
        session.close()


def get_all_store_names():
    session = SessionLocal()
    try:
        stores = session.query(StoreVisit.store_name).distinct().all()
        return [s[0] for s in stores]
    finally:
        session.close()


def get_last_visit_by_store(store_name):
    session = SessionLocal()
    try:
        return (
            session.query(StoreVisit)
            .filter(StoreVisit.store_name == store_name)
            .order_by(StoreVisit.visit_date.desc(), StoreVisit.visit_time.desc())
            .first()
        )
    finally:
        session.close()


def get_visits_by_user(username):
    session = SessionLocal()
    try:
        return (
            session.query(StoreVisit)
            .filter(StoreVisit.username == username)
            .order_by(StoreVisit.visit_date.desc(), StoreVisit.visit_time.desc())
            .all()
        )
    finally:
        session.close()


def update_lead_status(visit_id, new_status):
    session = SessionLocal()
    try:
        visit = session.query(StoreVisit).filter(StoreVisit.id == visit_id).first()
        if not visit:
            return False, "Visit not found"

        visit.lead_type = new_status
        session.commit()
        return True, "Status Updated"

    except Exception as e:
        session.rollback()
        return False, str(e)

    finally:
        session.close()

# -------------------------------------------------------------------
# Auth & Seed Data
# -------------------------------------------------------------------

def authenticate_user(username, password):
    session = SessionLocal()
    try:
        return (
            session.query(User)
            .filter(User.username == username, User.password == password)
            .first()
        )
    finally:
        session.close()


def create_initial_users():
    session = SessionLocal()
    try:
        users = [
            User(username="admin", password="admin123", role="ADMIN", full_name="Administrator"),
            User(username="sr_user", password="sr123", role="SR", full_name="Sales Representative"),
            User(username="Raju123", password="Raju123", role="SR", full_name="RAJU DAS"),
            User(username="Shubram123", password="Shubram123", role="SR", full_name="SHUBRAM KAR"),
        ]

        for user in users:
            if not session.query(User).filter(User.username == user.username).first():
                session.add(user)

        session.commit()

    except Exception as e:
        print("User seed error:", e)

    finally:
        session.close()
