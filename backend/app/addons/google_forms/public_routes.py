from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.addons.google_forms.schemas import GoogleFormSubmissionResponse, WebhookPayload
from app.addons.google_forms.service import GoogleFormService
from app.core.db import get_db

router = APIRouter(tags=["public-google-forms"])


@router.post("/webhooks/google-forms/{webhook_secret}", response_model=GoogleFormSubmissionResponse)
async def receive_webhook(
    webhook_secret: str,
    payload: WebhookPayload,
    db: Session = Depends(get_db),
):
    """
    Public webhook endpoint for Google Forms submissions.
    Called by Google Apps Script when form is submitted.
    """
    from app.core.realtime.manager import connection_manager
    from app.addons.google_forms.models import GoogleFormIntegration
    
    # Get integration to find workspace_id
    integration = db.query(GoogleFormIntegration).filter(
        GoogleFormIntegration.webhook_secret == webhook_secret
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid webhook secret"
        )
    
    # Process webhook
    service = GoogleFormService(db, integration.workspace_id)
    submission = service.process_webhook(webhook_secret, payload.email, payload.responses)
    
    # Broadcast to workspace
    await connection_manager.broadcast_to_workspace(
        integration.workspace_id,
        {
            "type": "google_form.submitted",
            "submission": {
                "id": submission.id,
                "integration_id": submission.integration_id,
                "booking_id": submission.booking_id,
                "status": submission.status,
                "error_message": submission.error_message,
            }
        }
    )
    
    return submission
