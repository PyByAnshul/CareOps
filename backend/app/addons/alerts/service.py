from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.addons.alerts.models import Alert


class AlertService:
    def __init__(self, db: Session, workspace_id: int):
        self.db = db
        self.workspace_id = workspace_id
    
    def list_alerts(self, include_dismissed: bool = False) -> List[Alert]:
        """List alerts for workspace."""
        query = self.db.query(Alert).filter(
            Alert.workspace_id == self.workspace_id
        )
        
        if not include_dismissed:
            query = query.filter(Alert.is_dismissed == False)
        
        return query.order_by(Alert.created_at.desc()).all()
    
    def dismiss_alert(self, alert_id: int) -> Alert:
        """Dismiss an alert."""
        alert = self.db.query(Alert).filter(
            Alert.id == alert_id,
            Alert.workspace_id == self.workspace_id,
        ).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found",
            )
        
        alert.is_dismissed = True
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def create_alert(
        self,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        link: str = None,
    ) -> Alert:
        """Create a new alert."""
        alert = Alert(
            workspace_id=self.workspace_id,
            type=alert_type,
            severity=severity,
            title=title,
            message=message,
            link=link,
            is_dismissed=False,
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
