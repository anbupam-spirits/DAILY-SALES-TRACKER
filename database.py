from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Time, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

# --- Configuration ---
# Default to SQLite for local development. 
# To use Postgres, set env var: DATABASE_URL=postgresql://user:pass@localhost/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///field_sales.db")

# Ensure we use the correct dialect for invalid URLs (e.g. if simple 'starts with' check logic is needed later)
# For now, standard SQLAlchemy URL handling applies.

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False) # Simple password for now
    role = Column(String, default="SR") # SR, ADMIN
    full_name = Column(String, nullable=True)

class StoreVisit(Base):
    __tablename__ = 'store_visits'

    id = Column(Integer, primary_key=True, autoincrement=True)
    visit_date = Column(Date, nullable=False)
    visit_time = Column(Time, nullable=False)
    sr_name = Column(String, nullable=False)
    username = Column(String, nullable=True) # Linked to User.username
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

# --- Engine & Session ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Creates tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
    create_initial_users()

def save_visit(data: dict):
    """
    Saves a visit dictionary to the database.
    Returns: (bool, message)
    """
    session = SessionLocal()
    try:
        # data["visit_date"] comes as a string 'YYYY-MM-DD' from app.py usually, 
        # but SQLAlchemy Date column expects a date object or valid ISO string.
        # We'll assume app.py passes standard python objects or we parse them here if needed.
        # Given app.py sends `current_date` as string from strftime, SQLA usually handles ISO strings for SQLite/Postgres.
        # But safest is to convert strictly or let SQLA handle it.
        
        # We need to map the list/dict from app.py to this model.
        # App.py currently uses a list `row_data`. We should change app.py to pass a dict
        # OR we map the list here. A dict is cleaner for the interface.
        
        visit = StoreVisit(
            visit_date=datetime.strptime(data['date'], "%Y-%m-%d").date(),
            visit_time=datetime.strptime(data['time'], "%H:%M:%S").time(),
            sr_name=data['sr_name'],
            username=data.get('username'),
            store_name=data['store_name'],
            visit_type=data['visit_type'],
            store_category=data['store_category'],
            phone_number=data['phone'],
            lead_type=data['lead_type'],
            follow_up_date=data['follow_up_date'],
            products=data['products'],
            order_details=data['order_details'],
            latitude=float(data['latitude']) if data['latitude'] else None,
            longitude=float(data['longitude']) if data['longitude'] else None,
            maps_url=data['maps_url'],
            location_recorded_answer=data['location_recorded_answer'],
            image_data=data['image_data']
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
    """
    Fetches all visits from the database.
    Returns: List of StoreVisit objects
    """
    session = SessionLocal()
    try:
        visits = session.query(StoreVisit).order_by(StoreVisit.visit_date.desc(), StoreVisit.visit_time.desc()).all()
        return visits
    except Exception as e:
        return []
    finally:
        session.close()

def get_all_store_names():
    """Returns a list of distinct store names."""
    session = SessionLocal()
    try:
        # distinct() on store_name
        stores = session.query(StoreVisit.store_name).distinct().all()
        # stores is a list of tuples like [('Store A',), ('Store B',)]
        return [s[0] for s in stores]
    except Exception:
        return []
    finally:
        session.close()

def get_last_visit_by_store(store_name):
    """Returns the most recent StoreVisit object for a given store name."""
    session = SessionLocal()
    try:
        visit = session.query(StoreVisit).filter(StoreVisit.store_name == store_name).order_by(StoreVisit.visit_date.desc(), StoreVisit.visit_time.desc()).first()
        return visit
    except Exception:
        return None
    finally:
        session.close()

def get_visits_by_user(username):
    """Fetches all visits for a specific user."""
    session = SessionLocal()
    try:
        visits = session.query(StoreVisit).filter(StoreVisit.username == username).order_by(StoreVisit.visit_date.desc(), StoreVisit.visit_time.desc()).all()
        return visits
    except Exception:
        return []
    finally:
        session.close()

def update_lead_status(visit_id, new_status):
    """Updates the lead status of a visit."""
    session = SessionLocal()
    try:
        visit = session.query(StoreVisit).filter(StoreVisit.id == visit_id).first()
        if visit:
            visit.lead_type = new_status
            session.commit()
            return True, "Status Updated"
        return False, "Visit not found"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

def authenticate_user(username, password):
    """Simple user authentication."""
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.username == username, User.password == password).first()
        return user
    finally:
        session.close()

def create_initial_users():
    """Seed the database with default users."""
    session = SessionLocal()
    try:
        users_to_add = [
            User(username="admin", password="admin123", role="ADMIN", full_name="Administrator"),
            User(username="sr_user", password="sr123", role="SR", full_name="Sales Representative"),
            User(username="Raju123", password="Raju123", role="SR", full_name="RAJU DAS"),
            User(username="Shubram123", password="Shubram123", role="SR", full_name="SHUBRAM KAR")
        ]
        
        for u in users_to_add:
            exists = session.query(User).filter(User.username == u.username).first()
            if not exists:
                session.add(u)
        
        session.commit()
    except Exception as e:
        print(f"Error seeding users: {e}")
    finally:
        session.close()
