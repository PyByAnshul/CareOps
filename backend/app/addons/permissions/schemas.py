from pydantic import BaseModel


class PermissionResponse(BaseModel):
    id: int
    name: str
    description: str | None
    module: str
    
    class Config:
        from_attributes = True


class AssignPermission(BaseModel):
    user_id: int
    permission_name: str


class RemovePermission(BaseModel):
    user_id: int
    permission_name: str
