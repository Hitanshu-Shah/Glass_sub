from sqlalchemy import create_engine, Column, Integer, String, Date, BLOB, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    contact = Column(String)
    photo_id = Column(BLOB, nullable=True)
    subscription_start_date = Column(Date)
    remaining_changes = Column(Integer)
    family_members = Column(JSON, nullable=True)
    validity_period = Column(Integer)
    plan = Column(String)

class ChangeLog(Base):
    __tablename__ = 'changes_log'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer)
    change_date = Column(Date)

def setup_database():
    engine = create_engine('sqlite:///subscriptions.db')
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    setup_database()
