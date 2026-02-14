import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.addons.forms.models import Form, FormSubmission
from app.addons.forms.schemas import (
    FormSubmissionCreate,
    FormSubmissionResponse,
    PublicFormResponse,
)
from app.addons.forms.service import FormService
from app.core.db import get_db

router = APIRouter(tags=["public-forms"])


@router.get("/forms/{token}", response_model=PublicFormResponse)
def get_public_form(token: str, db: Session = Depends(get_db)):
    """Get form by form token (public access)."""
    # Get form by token
    form = db.query(Form).filter(Form.token == token).first()
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found",
        )
    
    return PublicFormResponse(
        form_name=form.name,
        form_type=form.form_type,
        schema=form.schema,
        token=token,
    )


@router.post("/forms/{token}/submit", response_model=FormSubmissionResponse)
async def submit_form(
    token: str,
    submission_data: FormSubmissionCreate,
    db: Session = Depends(get_db),
):
    """Submit form answers (public access)."""
    from app.core.realtime.manager import connection_manager
    
    # Get form by token
    form = db.query(Form).filter(Form.token == token).first()
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found",
        )
    
    # Create submission with unique token
    submission_token = secrets.token_urlsafe(32)
    submission = FormSubmission(
        form_id=form.id,
        contact_email=submission_data.contact_email,
        answers=submission_data.answers,
        status="pending",
        token=submission_token,
    )
    
    db.add(submission)
    db.flush()
    
    # Use FormService to process submission based on form type
    service = FormService(db, form.workspace_id)
    submission = service.submit_answers(submission_token, submission_data.answers)
    
    # Broadcast to workspace
    await connection_manager.broadcast_to_workspace(
        form.workspace_id,
        {
            "type": "form.submitted",
            "form_type": form.form_type,
            "submission": {
                "id": submission.id,
                "form_id": submission.form_id,
                "contact_email": submission.contact_email,
                "status": submission.status,
                "booking_id": submission.booking_id,
                "inquiry_id": submission.inquiry_id,
                "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
            }
        }
    )
    
    return submission
