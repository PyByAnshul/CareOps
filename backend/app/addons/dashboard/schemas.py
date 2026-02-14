from pydantic import BaseModel


class DashboardSummary(BaseModel):
    bookings_today: int
    pending_bookings: int
    unread_conversations: int
    failed_automations: int
    active_alerts: int
