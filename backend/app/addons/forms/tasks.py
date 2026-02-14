import logging
from typing import Any, Dict

from app.core.db import SessionLocal
from app.core.jobs.base_tasks import BaseTask
from app.core.jobs.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(base=BaseTask, bind=True, max_retries=3)
def send_form_email_task(self, submission_id: int, workspace_id: int, form_url: str) -> Dict[str, Any]:
    """
    Send form link to customer via email.
    """
    from app.addons.forms.models import Form, FormSubmission
    from app.addons.integrations.providers.factory import ProviderFactory
    
    db = SessionLocal()
    try:
        # Get submission
        submission = db.query(FormSubmission).filter(FormSubmission.id == submission_id).first()
        if not submission:
            logger.error(f"Form submission {submission_id} not found")
            return {"success": False, "message": "Submission not found"}
        
        # Get form
        form = db.query(Form).filter(Form.id == submission.form_id).first()
        if not form:
            logger.error(f"Form {submission.form_id} not found")
            return {"success": False, "message": "Form not found"}
        
        # Get email provider
        provider = ProviderFactory.get_email_provider(workspace_id, db)
        
        if not provider:
            logger.warning(f"No email provider configured for workspace {workspace_id}")
            return {"success": False, "message": "No email provider configured"}
        
        # Compose email
        subject = f"Please complete: {form.name}"
        body = f"""
Hello,

Please complete the following form: {form.name}

Click here to fill out the form:
{form_url}

Thank you!

Best regards,
CareOps Team
        """
        
        # Send email
        email_result = provider.send_email(submission.contact_email, subject, body)
        
        if email_result["success"]:
            logger.info(f"Form email sent to {submission.contact_email}")
        else:
            logger.error(f"Failed to send form email: {email_result['message']}")
        
        return email_result
    
    except Exception as e:
        logger.error(f"send_form_email_task failed: {str(e)}")
        raise
    finally:
        db.close()
