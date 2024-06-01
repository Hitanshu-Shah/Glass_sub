import sys
import os
import json
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta
import streamlit as st
from database_setup import Base, Customer, ChangeLog

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Database setup
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

    family_members_list = [member.strip() for member in family_members.split(',')] if family_members else []
    family_members_json = json.dumps(family_members_list) if family_members_list else None

    try:
        new_customer = Customer(
            name=name,
            contact=contact,
            photo_id=photo if photo else None,
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
    customer_data = []
    for customer in customers:
        customer_data.append({
            "ID": customer.id,
            "Name": customer.name,
            "Contact": customer.contact,
            "Subscription Start Date": customer.subscription_start_date,
            "Remaining Changes": customer.remaining_changes,
            "Validity Period": customer.validity_period,
            "Plan": customer.plan,
            "Family Members": ", ".join(json.loads(customer.family_members)) if customer.family_members else ""
        })
    df = pd.DataFrame(customer_data)
    st.dataframe(df)

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
        if name and contact and plan:
            register_customer(name, contact, photo.read() if photo else None, family_members, plan)
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
