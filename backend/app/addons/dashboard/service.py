from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.addons.alerts.models import Alert
from app.addons.automation.models import AutomationEventLog
from app.addons.bookings.models import Booking
from app.addons.inbox.models import Conversation
from app.addons.inventory.models import Product


class DashboardService:
    def __init__(self, db: Session, workspace_id: int):
        self.db = db
        self.workspace_id = workspace_id
    
    def get_summary(self) -> dict:
        """Get dashboard summary metrics."""
        return {
            "bookings_today": self._count_bookings_today(),
            "pending_bookings": self._count_pending_bookings(),
            "unread_conversations": self._count_unread_conversations(),
            "failed_automations": self._count_failed_automations(),
            "active_alerts": self._count_active_alerts(),
        }
    
    def get_booking_stats(self) -> dict:
        """Get booking statistics for charts."""
        return {
            "byStatus": self._bookings_by_status(),
            "byWeek": self._bookings_by_week(),
        }
    
    def get_inventory_stats(self) -> dict:
        """Get inventory statistics for charts."""
        return {
            "stockStatus": self._stock_status(),
            "topProducts": self._top_products(),
        }
    
    def _count_bookings_today(self) -> int:
        """Count bookings created today."""
        today = date.today()
        return self.db.query(func.count(Booking.id)).filter(
            Booking.workspace_id == self.workspace_id,
            func.date(Booking.created_at) == today,
        ).scalar() or 0
    
    def _count_pending_bookings(self) -> int:
        """Count bookings with pending status."""
        return self.db.query(func.count(Booking.id)).filter(
            Booking.workspace_id == self.workspace_id,
            Booking.status == "pending",
        ).scalar() or 0
    
    def _count_unread_conversations(self) -> int:
        """Count active conversations (placeholder for unread logic)."""
        return self.db.query(func.count(Conversation.id)).filter(
            Conversation.workspace_id == self.workspace_id,
            Conversation.status == "active",
        ).scalar() or 0
    
    def _count_failed_automations(self) -> int:
        """Count failed automation logs."""
        return self.db.query(func.count(AutomationEventLog.id)).filter(
            AutomationEventLog.workspace_id == self.workspace_id,
            AutomationEventLog.status.in_(["failed", "partial"]),
        ).scalar() or 0
    
    def _count_active_alerts(self) -> int:
        """Count non-dismissed alerts."""
        return self.db.query(func.count(Alert.id)).filter(
            Alert.workspace_id == self.workspace_id,
            Alert.is_dismissed == False,
        ).scalar() or 0
    
    def _bookings_by_status(self) -> list:
        """Get booking counts grouped by status."""
        results = self.db.query(
            Booking.status,
            func.count(Booking.id).label('count')
        ).filter(
            Booking.workspace_id == self.workspace_id
        ).group_by(Booking.status).all()
        
        return [{"status": status, "count": count} for status, count in results]
    
    def _bookings_by_week(self) -> list:
        """Get booking counts for the last 7 days."""
        today = date.today()
        week_ago = today - timedelta(days=6)
        
        results = self.db.query(
            func.date(Booking.booking_date).label('day'),
            func.count(Booking.id).label('count')
        ).filter(
            Booking.workspace_id == self.workspace_id,
            Booking.booking_date >= week_ago,
            Booking.booking_date <= today
        ).group_by(func.date(Booking.booking_date)).all()
        
        # Create dict for easy lookup
        data_dict = {str(day): count for day, count in results}
        
        # Fill in missing days with 0
        week_data = []
        for i in range(7):
            day = week_ago + timedelta(days=i)
            day_str = day.strftime('%a')
            count = data_dict.get(str(day), 0)
            week_data.append({"day": day_str, "count": count})
        
        return week_data
    
    def _stock_status(self) -> list:
        """Get product counts by stock status."""
        products = self.db.query(Product).filter(
            Product.workspace_id == self.workspace_id
        ).all()
        
        in_stock = 0
        low_stock = 0
        out_of_stock = 0
        
        for product in products:
            if product.quantity_on_hand == 0:
                out_of_stock += 1
            elif product.quantity_on_hand <= product.min_quantity:
                low_stock += 1
            else:
                in_stock += 1
        
        return [
            {"status": "In Stock", "count": in_stock},
            {"status": "Low Stock", "count": low_stock},
            {"status": "Out of Stock", "count": out_of_stock},
        ]
    
    def _top_products(self) -> list:
        """Get top 5 products by stock quantity."""
        products = self.db.query(Product).filter(
            Product.workspace_id == self.workspace_id
        ).order_by(Product.quantity_on_hand.desc()).limit(5).all()
        
        return [{"name": p.name, "quantity": p.quantity_on_hand} for p in products]
