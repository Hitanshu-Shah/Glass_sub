import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Customer, ChangeLog, engine
from datetime import date, timedelta
import streamlit as st
import json

# Database connection
Session = sessionmaker(bind=engine)
session = Session()

def register_customer(name, contact, photo, family_members):
    subscription_start_date = date.today()
    remaining_changes = 3
    validity_period = 90  # days
    family_members_json = json.dumps(family_members)

    new_customer = Customer(
        name=name,
        contact=contact,
        photo_id=photo,
        subscription_start_date=subscription_start_date,
        remaining_changes=remaining_changes,
        family_members=family_members_json,
        validity_period=validity_period
    )
    session.add(new_customer)
    session.commit()
    st.success("Customer registered successfully!")

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
    st.success("Glass change logged successfully")

# Streamlit UI
st.title("Tempered Glass Subscription Service")

menu = ["Register Customer", "Log Glass Change"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register Customer":
    st.subheader("Register a New Customer")
    name = st.text_input("Name")
    contact = st.text_input("Contact")
    photo = st.file_uploader("Upload Photo ID", type=["jpg", "jpeg", "png"])
    family_members = st.text_area("Family Members (JSON format)")

    if st.button("Register"):
        if name and contact and photo and family_members:
            family_members_list = json.loads(family_members)
            register_customer(name, contact, photo.read(), family_members_list)
        else:
            st.error("Please fill all fields")

elif choice == "Log Glass Change":
    st.subheader("Log a Glass Change")
    customer_id = st.number_input("Customer ID", min_value=1)
    family_member_id = st.number_input("Family Member ID (if applicable)", min_value=0)

    if st.button("Log Change"):
        verify_and_log_change(customer_id, family_member_id if family_member_id != 0 else None)
