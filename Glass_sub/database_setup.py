from sqlalchemy import create_engine, Column, Integer, String, Date, BLOB, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    contact = Column(String)
    photo_id = Column(BLOB)
    subscription_start_date = Column(Date)
    remaining_changes = Column(Integer)
    family_members = Column(JSON)
    validity_period = Column(Integer)

class ChangeLog(Base):
    __tablename__ = 'changes_log'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer)
    change_date = Column(Date)

engine = create_engine('sqlite:///subscriptions.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
