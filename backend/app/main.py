import logging
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query

from app.core.app import create_app
from app.core.config import get_settings
from app.core.db import Base, SessionLocal, engine, init_db, get_db
from app.core.registry import register_addon_routers
from app.core.realtime.manager import connection_manager

logger = logging.getLogger(__name__)

_settings = get_settings()
fastapi_app: FastAPI = create_app(_settings)


def bootstrap() -> None:
    """
    Perform core bootstrapping:
    - initialize DB engine
    - create tables
    - seed permissions
    - register event handlers
    - auto-register addon routers
    """
    init_db()
    
    # Import models to ensure they're registered with Base
    from app.addons.users.models import User  # noqa: F401
    from app.addons.workspace.models import Workspace  # noqa: F401
    from app.addons.permissions.models import Permission, UserPermission  # noqa: F401
    from app.addons.bookings.models import Booking  # noqa: F401
    from app.addons.automation.models import AutomationEventLog  # noqa: F401
    from app.addons.integrations.models import Integration  # noqa: F401
    from app.addons.inbox.models import Conversation, Message  # noqa: F401
    from app.addons.alerts.models import Alert  # noqa: F401
    from app.addons.forms.models import Form, FormSubmission  # noqa: F401
    from app.addons.services.models import Service, ServiceAvailability  # noqa: F401
    from app.addons.inventory.models import Product, ProcurementRule, ProcurementOrder, StockMovement  # noqa: F401
    from app.addons.contacts.models import Partner  # noqa: F401
    from app.addons.google_forms.models import GoogleFormIntegration, GoogleFormSubmission  # noqa: F401
    from app.addons.calendar.models import CalendarSettings  # noqa: F401
    from app.addons.webex.models import WebexMeeting  # noqa: F401
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Seed permissions and default admin
    from app.addons.permissions.service import PermissionService
    from app.addons.users.service import UserService
    from app.addons.users.schemas import UserRegister
    from app.addons.users.models import User
    
    db = SessionLocal()
    try:
        # Seed permissions
        service = PermissionService(db)
        service.seed_permissions()
        logger.info("Permissions seeded")
        
        # Create default admin user
        admin_email = "admin@careops.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            user_service = UserService(db)
            admin_data = UserRegister(
                email=admin_email,
                password="admin@123",
                workspace_id=1,
                role="owner"
            )
            user_service.create_user(admin_data)
            logger.info("Default admin user created successfully")
        else:
            logger.info("Default admin user already exists")
    finally:
        db.close()
    
    # Register event handlers
    from app.core.events.handlers import register_automation_handler
    register_automation_handler()
    
    # Import calendar events to register handlers
    import app.addons.calendar  # noqa: F401
    
    register_addon_routers(fastapi_app)
    
    # Explicitly register dashboard router
    from app.addons.dashboard import routes as dashboard_routes
    fastapi_app.include_router(dashboard_routes.router, prefix="/api/dashboard", tags=["dashboard"])
    print("Dashboard router registered at /api/dashboard")
    print(f"Dashboard routes: {[route.path for route in dashboard_routes.router.routes]}")
    
    # Register public routes
    from app.addons.forms import public_routes
    fastapi_app.include_router(public_routes.router, prefix="/public")
    
    # Register Google Forms routes
    from app.addons.google_forms import routes as google_forms_routes
    from app.addons.google_forms import public_routes as google_forms_public_routes
    fastapi_app.include_router(google_forms_routes.router, prefix="/api/google-forms", tags=["google-forms"])
    fastapi_app.include_router(google_forms_public_routes.router, prefix="/api/public", tags=["public-google-forms"])
    
    # Register Calendar routes
    from app.addons.calendar import routes as calendar_routes
    fastapi_app.include_router(calendar_routes.router, prefix="/api/calendar", tags=["calendar"])
    
    # Register Webex routes
    from app.addons.webex import routes as webex_routes
    fastapi_app.include_router(webex_routes.router, prefix="/api/webex", tags=["webex"])
    
    logger.info("Application bootstrap complete")


bootstrap()

# Print all registered routes for debugging
print("\n=== All Registered Routes ===")
for route in fastapi_app.routes:
    if hasattr(route, 'path'):
        print(f"{route.methods if hasattr(route, 'methods') else 'N/A'} {route.path}")
print("===========================\n")

# Export as 'app' for uvicorn
app = fastapi_app


@app.get("/health", tags=["health"])
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """
    WebSocket endpoint for real-time updates.
    
    Connect with: ws://localhost:8000/ws?token=YOUR_JWT_TOKEN
    """
    db = SessionLocal()
    connection = None
    
    try:
        # Authenticate user
        user = await connection_manager.authenticate(websocket, token, db)
        
        if not user:
            await websocket.close(code=1008, reason="Authentication failed")
            return
        
        # Connect user
        connection = await connection_manager.connect(websocket, user)
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back for now (can add ping/pong or other commands)
            await connection.send_json({
                "type": "echo",
                "message": data,
            })
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        if connection:
            connection_manager.disconnect(connection)
        db.close()

