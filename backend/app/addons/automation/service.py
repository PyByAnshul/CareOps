from typing import List

from sqlalchemy.orm import Session

from app.addons.automation.models import AutomationEventLog


class AutomationService:
    def __init__(self, db: Session, workspace_id: int):
        self.db = db
        self.workspace_id = workspace_id
    
    def get_logs(self) -> List[AutomationEventLog]:
        """Get all automation logs for the workspace."""
        return self.db.query(AutomationEventLog).filter(
            AutomationEventLog.workspace_id == self.workspace_id
        ).order_by(AutomationEventLog.created_at.desc()).all()
