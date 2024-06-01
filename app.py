import sys
import os
from sqlalchemy import create_engine, Column, Integer, String, Date, BLOB, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta
import streamlit as st

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Database setup
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
    plan = Column(String)

class ChangeLog(Base):
    __tablename__ = 'changes_log'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer)
    change_date = Column(Date)

engine = create_engine('sqlite:///subscriptions.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def register_customer(name, contact, photo, family_members, plan):
    subscription_start_date = date.today()
    
    # Set remaining changes and validity period based on the selected plan
    if plan == "3 Glass Changes in 3 Months - 3000 Rs":
        remaining_changes = 3
        validity_period = 90
    elif plan == "6 Glass Changes in 6 Months - 6000 Rs":
        remaining_changes = 6
        validity_period = 180

    family_members_list = [member.strip() for member in family_members.split(',')]
    family_members_json = json.dumps(family_members_list)  # Ensure it's JSON formatted

    try:
        new_customer = Customer(
            name=name,
            contact=contact,
            photo_id=photo,
            subscription_start_date=subscription_start_date,
            remaining_changes=remaining_changes,
            family_members=family_members_json,
            validity_period=validity_period,
            plan=plan
        )
        session.add(new_customer)
        session.commit()
        st.success("Customer registered successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def verify_and_log_change(customer_id, family_member_id=None):
    customer = session.query(Customer).filter_by(id=customer_id).first()
    if not customer:
        st.error("Customer not found")
        return

    # Check subscription validity
    if date.today() > customer.subscription_start_date + timedelta(days=customer.validity_period):
        st.error("Subscription expired")
        return

    # Check remaining changes
    if customer.remaining_changes <= 0:
        st.error("No remaining changes")
        return

    # Log the change
    new_change = ChangeLog(customer_id=customer_id, change_date=date.today())
    session.add(new_change)
    customer.remaining_changes -= 1
    session.commit()
    st.success("Glass change logged successfully!")

def get_customers():
    customers = session.query(Customer).all()
    customer_list = {}
    for customer in customers:
        customer_list[customer.id] = customer.name
    return customer_list

def display_customers():
    customers = session.query(Customer).all()
    for customer in customers:
        st.write({
            "ID": customer.id,
            "Name": customer.name,
            "Contact": customer.contact,
            "Subscription Start Date": customer.subscription_start_date,
            "Remaining Changes": customer.remaining_changes,
            "Validity Period": customer.validity_period,
            "Plan": customer.plan,
            "Family Members": json.loads(customer.family_members)
        })

# Streamlit UI
st.title("Tempered Glass Subscription Service")

menu = ["Register Customer", "Log Glass Change", "View Customers"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register Customer":
    st.subheader("Register a New Customer")
    name = st.text_input("Name")
    contact = st.text_input("Contact")
    photo = st.file_uploader("Upload Photo ID", type=["jpg", "jpeg", "png"])
    family_members = st.text_area("Family Members (comma-separated)")
    plan = st.selectbox("Select Plan", ["3 Glass Changes in 3 Months - 3000 Rs", "6 Glass Changes in 6 Months - 6000 Rs"])

    if st.button("Register"):
        if name and contact and photo and family_members and plan:
            register_customer(name, contact, photo.read(), family_members, plan)
        else:
            st.error("Please fill all fields")

elif choice == "Log Glass Change":
    st.subheader("Log a Glass Change")
    customers = get_customers()
    if customers:
        customer_id = st.selectbox("Select Customer", options=list(customers.keys()), format_func=lambda x: customers[x])
        family_member_id = st.number_input("Family Member ID (if applicable)", min_value=0)

        if st.button("Log Change"):
            verify_and_log_change(customer_id, family_member_id if family_member_id != 0 else None)
    else:
        st.warning("No customers registered yet.")

elif choice == "View Customers":
    st.subheader("Registered Customers")
    display_customers()
