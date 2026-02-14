from sqlalchemy.orm import Session

from app.addons.workspace.models import Workspace
from app.addons.workspace.schemas import WorkspaceCreate


class WorkspaceService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_workspace(self, workspace_data: WorkspaceCreate) -> Workspace:
        workspace = Workspace(
            name=workspace_data.name,
            timezone=workspace_data.timezone,
            is_active=True,
        )
        
        self.db.add(workspace)
        self.db.commit()
        self.db.refresh(workspace)
        
        return workspace
    
    def get_workspace_by_id(self, workspace_id: int) -> Workspace:
        return self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
