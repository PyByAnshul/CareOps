from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.addons.bookings.schemas import BookingCreate, BookingResponse, BookingUpdate
from app.addons.bookings.service import BookingService
from app.addons.users.models import User
from app.addons.workspace.models import Workspace
from app.core.db import get_db
from app.core.security.deps import get_current_workspace, require_active_user
from app.core.security.permissions import PermissionChecker

router = APIRouter(tags=["bookings"])


@router.get("/", response_model=List[BookingResponse])
def list_bookings(
    status: str | None = None,
    current_user: User = Depends(PermissionChecker("bookings.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = BookingService(db, workspace.id, current_user.id)
    return service.list_bookings(status=status)


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(PermissionChecker("bookings.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    from app.core.realtime.manager import connection_manager
    
    service = BookingService(db, workspace.id, current_user.id)
    booking = service.create_booking(booking_data)
    
    # Broadcast to workspace
    await connection_manager.broadcast_to_workspace(
        workspace.id,
        {
            "type": "booking.created",
            "booking": BookingResponse.model_validate(booking).model_dump(mode="json"),
        }
    )
    
    return booking


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    current_user: User = Depends(PermissionChecker("bookings.read")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = BookingService(db, workspace.id, current_user.id)
    return service.get_booking(booking_id)


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    current_user: User = Depends(PermissionChecker("bookings.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    from app.core.realtime.manager import connection_manager
    
    service = BookingService(db, workspace.id, current_user.id)
    booking = service.update_booking(booking_id, booking_data)
    
    # Broadcast to workspace
    await connection_manager.broadcast_to_workspace(
        workspace.id,
        {
            "type": "booking.updated",
            "booking": BookingResponse.model_validate(booking).model_dump(mode="json"),
        }
    )
    
    return booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(
    booking_id: int,
    current_user: User = Depends(PermissionChecker("bookings.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = BookingService(db, workspace.id, current_user.id)
    service.delete_booking(booking_id)


@router.post("/{booking_id}/confirm", response_model=BookingResponse)
async def confirm_booking(
    booking_id: int,
    current_user: User = Depends(PermissionChecker("bookings.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = BookingService(db, workspace.id, current_user.id)
    booking = service.confirm_booking(booking_id)
    return booking


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: int,
    current_user: User = Depends(PermissionChecker("bookings.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = BookingService(db, workspace.id, current_user.id)
    booking = service.cancel_booking(booking_id)
    return booking


@router.post("/{booking_id}/complete", response_model=BookingResponse)
async def complete_booking(
    booking_id: int,
    current_user: User = Depends(PermissionChecker("bookings.write")),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    service = BookingService(db, workspace.id, current_user.id)
    booking = service.complete_booking(booking_id)
    return booking
