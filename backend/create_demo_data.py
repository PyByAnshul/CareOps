#!/usr/bin/env python3
"""
Demo data script for CareOps

Run this script to populate the database with demo data:
    python create_demo_data.py
"""

import sys
import os
from datetime import datetime, date, time, timedelta
import json
import uuid
import secrets

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import SessionLocal, engine, Base
from app.core.security.hashing import hash_password

# Import all models
from app.addons.users.models import User
from app.addons.workspace.models import Workspace
from app.addons.contacts.models import Partner
from app.addons.services.models import Service, ServiceAvailability
from app.addons.bookings.models import Booking
from app.addons.forms.models import Form, FormSubmission
from app.addons.inventory.models import Product, ProcurementRule, ProcurementOrder, StockMovement
from app.addons.permissions.models import Permission, UserPermission


def create_demo_data():
    """Create comprehensive demo data for CareOps"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Creating CareOps demo data...")
        
        # 1. Create Workspace
        print("Creating workspace...")
        workspace = Workspace(
            name="CareOps Demo Clinic",
            timezone="America/New_York",
            is_active=True
        )
        db.add(workspace)
        db.commit()
        db.refresh(workspace)
        
        # 2. Create Users (skip if already exist)
        print("Creating users...")
        users_data = [
            {
                "email": "admin@careops.com",
                "password": "admin123",
                "role": "owner"
            },
            {
                "email": "staff@careops.com", 
                "password": "staff123",
                "role": "staff"
            },
            {
                "email": "nurse@careops.com",
                "password": "nurse123", 
                "role": "staff"
            }
        ]
        
        users = []
        for user_data in users_data:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if existing_user:
                print(f"User {user_data['email']} already exists, skipping...")
                users.append(existing_user)
                continue
                
            user = User(
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                role=user_data["role"],
                workspace_id=workspace.id,
                is_active=True
            )
            db.add(user)
            users.append(user)
        
        db.commit()
        for user in users:
            if user.id is None:
                db.refresh(user)
        
        # 3. Create Services
        print("Creating services...")
        services_data = [
            {"name": "General Consultation", "duration": 30},
            {"name": "Physical Therapy", "duration": 60},
            {"name": "Blood Test", "duration": 15},
            {"name": "X-Ray", "duration": 20},
            {"name": "Dental Cleaning", "duration": 45},
            {"name": "Eye Exam", "duration": 30},
            {"name": "Vaccination", "duration": 10}
        ]
        
        services = []
        for service_data in services_data:
            service = Service(
                workspace_id=workspace.id,
                name=service_data["name"],
                duration_minutes=service_data["duration"],
                is_active=True
            )
            db.add(service)
            services.append(service)
        
        db.commit()
        for service in services:
            db.refresh(service)
        
        # 4. Create Service Availability (Mon-Fri, 9AM-5PM)
        print("Creating service availability...")
        for service in services:
            for day in range(5):  # Monday to Friday
                availability = ServiceAvailability(
                    service_id=service.id,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(17, 0)
                )
                db.add(availability)
        
        db.commit()
        
        # 5. Create Contacts/Partners
        print("Creating contacts...")
        contacts_data = [
            {
                "name": "John Smith",
                "email": "john.smith@email.com",
                "phone": "+1-555-0101",
                "company": None,
                "type": "customer"
            },
            {
                "name": "Emily Davis",
                "email": "emily.davis@email.com", 
                "phone": "+1-555-0102",
                "company": None,
                "type": "customer"
            },
            {
                "name": "Robert Wilson",
                "email": "robert.wilson@email.com",
                "phone": "+1-555-0103", 
                "company": None,
                "type": "customer"
            },
            {
                "name": "Medical Supplies Inc",
                "email": "orders@medsupplies.com",
                "phone": "+1-555-0201",
                "company": "Medical Supplies Inc",
                "type": "supplier"
            }
        ]
        
        contacts = []
        for contact_data in contacts_data:
            contact = Partner(
                workspace_id=workspace.id,
                name=contact_data["name"],
                email=contact_data["email"],
                phone=contact_data["phone"],
                company=contact_data["company"],
                partner_type=contact_data["type"],
                is_active=True
            )
            db.add(contact)
            contacts.append(contact)
        
        db.commit()
        for contact in contacts:
            db.refresh(contact)
        
        # 6. Create Bookings
        print("Creating bookings...")
        customer_contacts = [c for c in contacts if c.partner_type == "customer"]
        
        bookings_data = []
        base_date = date.today()
        
        # Past bookings
        for i in range(10):
            booking_date = base_date - timedelta(days=i+1)
            bookings_data.append({
                "customer": customer_contacts[i % len(customer_contacts)],
                "service": services[i % len(services)],
                "date": booking_date,
                "time": time(9 + (i % 8), 0),
                "status": "completed"
            })
        
        # Future bookings
        for i in range(8):
            booking_date = base_date + timedelta(days=i+1)
            bookings_data.append({
                "customer": customer_contacts[i % len(customer_contacts)],
                "service": services[i % len(services)],
                "date": booking_date,
                "time": time(10 + (i % 6), 0),
                "status": "confirmed" if i < 5 else "pending"
            })
        
        for booking_data in bookings_data:
            booking = Booking(
                workspace_id=workspace.id,
                service_id=booking_data["service"].id,
                customer_name=booking_data["customer"].name,
                customer_email=booking_data["customer"].email,
                booking_date=booking_data["date"],
                booking_time=booking_data["time"],
                status=booking_data["status"],
                notes=f"Booking for {booking_data['service'].name}",
                created_by=users[0].id
            )
            db.add(booking)
        
        db.commit()
        
        # 7. Create Forms
        print("Creating forms...")
        
        # Booking form with required fields
        booking_form = Form(
            workspace_id=workspace.id,
            name="Appointment Booking",
            form_type="booking",
            schema={
                "fields": [
                    {
                        "type": "text",
                        "label": "customer_name",
                        "required": True,
                        "placeholder": "Enter your full name"
                    },
                    {
                        "type": "select",
                        "label": "service_id",
                        "required": True,
                        "options": [str(s.id) for s in services[:3]]
                    },
                    {
                        "type": "date",
                        "label": "booking_date",
                        "required": True
                    },
                    {
                        "type": "text",
                        "label": "booking_time",
                        "required": True,
                        "placeholder": "HH:MM (e.g., 14:30)"
                    },
                    {
                        "type": "textarea",
                        "label": "notes",
                        "required": False,
                        "placeholder": "Any special requirements"
                    },
                    {
                        "type": "text",
                        "label": "Insurance Provider",
                        "required": False,
                        "placeholder": "Your insurance company"
                    }
                ]
            },
            is_active=True,
            token=secrets.token_urlsafe(32)
        )
        db.add(booking_form)
        
        # Inquiry form
        inquiry_form = Form(
            workspace_id=workspace.id,
            name="General Inquiry",
            form_type="inquiry",
            schema={
                "fields": [
                    {
                        "type": "text",
                        "label": "customer_name",
                        "required": True,
                        "placeholder": "Your name"
                    },
                    {
                        "type": "text",
                        "label": "subject",
                        "required": True,
                        "placeholder": "Subject of inquiry"
                    },
                    {
                        "type": "textarea",
                        "label": "message",
                        "required": True,
                        "placeholder": "Your message"
                    }
                ]
            },
            is_active=True,
            token=secrets.token_urlsafe(32)
        )
        db.add(inquiry_form)
        
        # Quote request form
        quote_form = Form(
            workspace_id=workspace.id,
            name="Request a Quote",
            form_type="quote",
            schema={
                "fields": [
                    {
                        "type": "text",
                        "label": "customer_name",
                        "required": True,
                        "placeholder": "Your name"
                    },
                    {
                        "type": "text",
                        "label": "subject",
                        "required": True,
                        "placeholder": "Service needed"
                    },
                    {
                        "type": "textarea",
                        "label": "message",
                        "required": True,
                        "placeholder": "Describe your requirements"
                    }
                ]
            },
            is_active=True,
            token=secrets.token_urlsafe(32)
        )
        db.add(quote_form)
        
        db.commit()
        db.refresh(booking_form)
        db.refresh(inquiry_form)
        db.refresh(quote_form)
        
        # 8. Create Form Submissions and Inquiries
        print("Creating form submissions...")
        from app.addons.forms.models import Inquiry
        
        # Inquiry submissions
        for i, contact in enumerate(customer_contacts[:2]):
            inquiry_submission = FormSubmission(
                form_id=inquiry_form.id,
                contact_email=contact.email,
                answers={
                    "customer_name": contact.name,
                    "subject": "Question about services",
                    "message": "I would like to know more about your services and pricing."
                },
                status="completed",
                token=str(uuid.uuid4()),
                submitted_at=datetime.utcnow() - timedelta(days=i+2)
            )
            db.add(inquiry_submission)
            db.flush()
            
            # Create inquiry record
            inquiry = Inquiry(
                workspace_id=workspace.id,
                form_submission_id=inquiry_submission.id,
                customer_name=contact.name,
                customer_email=contact.email,
                inquiry_type="inquiry",
                subject="Question about services",
                message="I would like to know more about your services and pricing.",
                status="new" if i == 0 else "contacted"
            )
            db.add(inquiry)
            inquiry_submission.inquiry_id = inquiry.id
        
        db.commit()
        
        # 9. Create Inventory Products
        print("Creating inventory products...")
        products_data = [
            {
                "name": "Disposable Gloves",
                "sku": "GLV-001",
                "description": "Latex-free disposable examination gloves",
                "quantity": 500.0,
                "min_quantity": 100.0,
                "unit": "box"
            },
            {
                "name": "Surgical Masks",
                "sku": "MSK-001", 
                "description": "3-ply surgical face masks",
                "quantity": 200.0,
                "min_quantity": 50.0,
                "unit": "box"
            },
            {
                "name": "Syringes 5ml",
                "sku": "SYR-005",
                "description": "Sterile disposable syringes 5ml",
                "quantity": 150.0,
                "min_quantity": 30.0,
                "unit": "pack"
            },
            {
                "name": "Bandages",
                "sku": "BND-001",
                "description": "Adhesive bandages assorted sizes",
                "quantity": 75.0,
                "min_quantity": 20.0,
                "unit": "box"
            }
        ]
        
        products = []
        for product_data in products_data:
            product = Product(
                workspace_id=workspace.id,
                name=product_data["name"],
                sku=product_data["sku"],
                description=product_data["description"],
                quantity_on_hand=product_data["quantity"],
                min_quantity=product_data["min_quantity"],
                unit_of_measure=product_data["unit"],
                is_active=True
            )
            db.add(product)
            products.append(product)
        
        db.commit()
        for product in products:
            db.refresh(product)
        
        # 10. Create Stock Movements
        print("Creating stock movements...")
        for i, product in enumerate(products[:2]):
            # Incoming stock
            movement_in = StockMovement(
                workspace_id=workspace.id,
                product_id=product.id,
                quantity=50.0,
                movement_type="in",
                reference=f"PO-{1000+i}",
                notes="Stock replenishment",
                created_by=users[0].id
            )
            db.add(movement_in)
            
            # Outgoing stock
            movement_out = StockMovement(
                workspace_id=workspace.id,
                product_id=product.id,
                quantity=-25.0,
                movement_type="out",
                reference=f"USAGE-{2000+i}",
                notes="Used in patient care",
                created_by=users[1].id
            )
            db.add(movement_out)
        
        db.commit()
        
        print("Demo data created successfully!")
        print("")
        print("Login Credentials:")
        print("Admin: admin@careops.com / admin123")
        print("Staff: staff@careops.com / staff123")
        print("Nurse: nurse@careops.com / nurse123")
        print("")
        print("Data Summary:")
        print(f"- 1 Workspace: {workspace.name}")
        print(f"- {len(users)} Users")
        print(f"- {len(services)} Services")
        print(f"- {len(contacts)} Contacts")
        print(f"- {len(bookings_data)} Bookings")
        print(f"- 3 Forms (Booking, Inquiry, Quote)")
        print(f"- {len(products)} Products")
        print("")
        print(f"Form Tokens:")
        print(f"- Booking Form: {booking_form.token}")
        print(f"- Inquiry Form: {inquiry_form.token}")
        print(f"- Quote Form: {quote_form.token}")
        
    except Exception as e:
        print(f"Error creating demo data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_demo_data()