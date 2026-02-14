"""
Helper script to set up email integration for a workspace.

Usage:
    python setup_email.py
"""

from app.addons.integrations.models import Integration
from app.core.db import SessionLocal


def setup_smtp_integration(workspace_id: int):
    """Set up SMTP email integration for a workspace."""
    
    db = SessionLocal()
    try:
        # Example SMTP configuration (Gmail)
        config = {
            "host": "smtp.gmail.com",
            "port": 587,
            "username": "your-email@gmail.com",
            "password": "your-app-password",  # Use app-specific password
            "from_email": "your-email@gmail.com",
            "use_tls": True,
        }
        
        # Deactivate existing email integrations
        existing = db.query(Integration).filter(
            Integration.workspace_id == workspace_id,
            Integration.integration_type == "email",
        ).all()
        
        for integration in existing:
            integration.is_active = False
        
        # Create new integration
        integration = Integration(
            workspace_id=workspace_id,
            integration_type="email",
            provider="smtp",
            config=config,
            is_active=True,
        )
        
        db.add(integration)
        db.commit()
        
        print(f"✓ SMTP integration created for workspace {workspace_id}")
        print(f"  Integration ID: {integration.id}")
        print(f"  Provider: {integration.provider}")
        print(f"  From: {config['from_email']}")
        
    except Exception as e:
        print(f"✗ Failed to create integration: {str(e)}")
        db.rollback()
    finally:
        db.close()


def setup_sendgrid_integration(workspace_id: int):
    """Set up SendGrid email integration for a workspace."""
    
    db = SessionLocal()
    try:
        config = {
            "api_key": "your-sendgrid-api-key",
            "from_email": "noreply@yourdomain.com",
        }
        
        # Deactivate existing email integrations
        existing = db.query(Integration).filter(
            Integration.workspace_id == workspace_id,
            Integration.integration_type == "email",
        ).all()
        
        for integration in existing:
            integration.is_active = False
        
        # Create new integration
        integration = Integration(
            workspace_id=workspace_id,
            integration_type="email",
            provider="sendgrid",
            config=config,
            is_active=True,
        )
        
        db.add(integration)
        db.commit()
        
        print(f"✓ SendGrid integration created for workspace {workspace_id}")
        print(f"  Integration ID: {integration.id}")
        print(f"  Provider: {integration.provider}")
        
    except Exception as e:
        print(f"✗ Failed to create integration: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Email Integration Setup")
    print("=" * 60)
    
    workspace_id = int(input("Enter workspace ID: "))
    provider = input("Choose provider (smtp/sendgrid): ").lower()
    
    if provider == "smtp":
        setup_smtp_integration(workspace_id)
    elif provider == "sendgrid":
        setup_sendgrid_integration(workspace_id)
    else:
        print("Invalid provider. Choose 'smtp' or 'sendgrid'")
