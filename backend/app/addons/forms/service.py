import secrets
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.addons.forms.models import Form, FormSubmission, Inquiry
from app.addons.forms.schemas import FormCreate
from app.addons.bookings.models import Booking


class FormService:
    def __init__(self, db: Session, workspace_id: int):
        self.db = db
        self.workspace_id = workspace_id
    
    def create_form(self, form_data: FormCreate) -> Form:
        """Create a new form template."""
        # Generate unique token for public access
        token = secrets.token_urlsafe(32)
        
        form = Form(
            workspace_id=self.workspace_id,
            name=form_data.name,
            form_type=form_data.form_type,
            schema=form_data.schema,
            is_active=True,
            token=token,
        )
        
        self.db.add(form)
        self.db.commit()
        self.db.refresh(form)
        
        return form
    
    def list_forms(self) -> List[Form]:
        """List all forms for workspace."""
        return self.db.query(Form).filter(
            Form.workspace_id == self.workspace_id
        ).order_by(Form.created_at.desc()).all()
    
    def get_form(self, form_id: int) -> Form:
        """Get form by ID with workspace check."""
        form = self.db.query(Form).filter(
            Form.id == form_id,
            Form.workspace_id == self.workspace_id,
        ).first()
        
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found",
            )
        
        return form
    
    def create_submission(
        self,
        form_id: int,
        contact_email: str,
        booking_id: Optional[int] = None,
    ) -> FormSubmission:
        """Create a form submission with token."""
        form = self.get_form(form_id)
        
        # Generate unique token
        token = secrets.token_urlsafe(32)
        
        submission = FormSubmission(
            form_id=form_id,
            booking_id=booking_id,
            contact_email=contact_email,
            answers={},
            status="pending",
            token=token,
        )
        
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        
        return submission
    
    def get_submission_by_token(self, token: str) -> FormSubmission:
        """Get submission by token (public access)."""
        submission = self.db.query(FormSubmission).filter(
            FormSubmission.token == token
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form submission not found",
            )
        
        return submission
    
    def submit_answers(self, token: str, answers: dict) -> FormSubmission:
        """Submit answers to a form and process based on form type."""
        submission = self.get_submission_by_token(token)
        
        if submission.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Form already submitted",
            )
        
        # Get form to check type
        form = self.db.query(Form).filter(Form.id == submission.form_id).first()
        
        submission.answers = answers
        submission.status = "completed"
        submission.submitted_at = datetime.utcnow()
        
        # Process based on form type
        if form.form_type == "booking":
            # Create booking with pending status
            booking = self._create_booking_from_submission(submission, answers)
            submission.booking_id = booking.id
        elif form.form_type in ["inquiry", "quote"]:
            # Create inquiry
            inquiry = self._create_inquiry_from_submission(submission, answers, form.form_type)
            submission.inquiry_id = inquiry.id
        
        self.db.commit()
        self.db.refresh(submission)
        
        return submission
    
    def _create_booking_from_submission(self, submission: FormSubmission, answers: dict) -> Booking:
        """Create a booking from form submission with proper field mapping."""
        from datetime import date, time
        
        # Required booking fields mapping
        customer_name = answers.get("customer_name") or answers.get("name") or "Unknown"
        service_id = answers.get("service_id")
        booking_date_str = answers.get("booking_date")
        booking_time_str = answers.get("booking_time")
        
        # Parse date and time
        try:
            booking_date = date.fromisoformat(booking_date_str) if booking_date_str else date.today()
        except (ValueError, TypeError):
            booking_date = date.today()
        
        try:
            if booking_time_str:
                if isinstance(booking_time_str, str):
                    # Handle both HH:MM and HH:MM:SS formats
                    time_parts = booking_time_str.split(":")
                    booking_time = time(int(time_parts[0]), int(time_parts[1]))
                else:
                    booking_time = time(9, 0)
            else:
                booking_time = time(9, 0)
        except (ValueError, TypeError, IndexError):
            booking_time = time(9, 0)
        
        # Collect custom fields as notes
        custom_fields = []
        for key, value in answers.items():
            if key not in ["customer_name", "name", "service_id", "booking_date", "booking_time", "notes"]:
                custom_fields.append(f"{key}: {value}")
        
        notes = answers.get("notes", "")
        if custom_fields:
            notes = notes + "\n\nAdditional Information:\n" + "\n".join(custom_fields) if notes else "\n".join(custom_fields)
        
        booking = Booking(
            workspace_id=self.workspace_id,
            service_id=service_id,
            customer_name=customer_name,
            customer_email=submission.contact_email,
            booking_date=booking_date,
            booking_time=booking_time,
            status="pending",
            notes=notes.strip() if notes else None,
            created_by=1,  # System user
        )
        
        self.db.add(booking)
        self.db.flush()
        return booking
    
    def _create_inquiry_from_submission(self, submission: FormSubmission, answers: dict, inquiry_type: str) -> Inquiry:
        """Create an inquiry from form submission."""
        inquiry = Inquiry(
            workspace_id=self.workspace_id,
            form_submission_id=submission.id,
            customer_name=answers.get("customer_name", "Unknown"),
            customer_email=submission.contact_email,
            inquiry_type=inquiry_type,
            subject=answers.get("subject"),
            message=answers.get("message"),
            status="new",
        )
        
        self.db.add(inquiry)
        self.db.flush()
        return inquiry
    
    def list_submissions(self, form_id: Optional[int] = None) -> List[FormSubmission]:
        """List submissions for workspace."""
        query = self.db.query(FormSubmission).join(Form).filter(
            Form.workspace_id == self.workspace_id
        )
        
        if form_id:
            query = query.filter(FormSubmission.form_id == form_id)
        
        return query.order_by(FormSubmission.created_at.desc()).all()

    def list_inquiries(self, status: Optional[str] = None) -> List[Inquiry]:
        """List inquiries for workspace."""
        query = self.db.query(Inquiry).filter(
            Inquiry.workspace_id == self.workspace_id
        )
        
        if status:
            query = query.filter(Inquiry.status == status)
        
        return query.order_by(Inquiry.created_at.desc()).all()
    
    def update_inquiry(self, inquiry_id: int, status: Optional[str] = None, assigned_to: Optional[int] = None) -> Inquiry:
        """Update inquiry status or assignment."""
        inquiry = self.db.query(Inquiry).filter(
            Inquiry.id == inquiry_id,
            Inquiry.workspace_id == self.workspace_id,
        ).first()
        
        if not inquiry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inquiry not found",
            )
        
        if status:
            inquiry.status = status
        if assigned_to is not None:
            inquiry.assigned_to = assigned_to
        
        self.db.commit()
        self.db.refresh(inquiry)
        
        return inquiry

    
    def update_form(self, form_id: int, form_data: FormCreate) -> Form:
        """Update an existing form."""
        form = self.get_form(form_id)
        
        form.name = form_data.name
        form.form_type = form_data.form_type
        form.schema = form_data.schema
        
        self.db.commit()
        self.db.refresh(form)
        
        return form
