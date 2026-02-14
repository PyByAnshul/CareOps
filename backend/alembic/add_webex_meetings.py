"""Add webex_meetings table

Run this migration:
    python backend/alembic/add_webex_meetings.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import engine, Base
from app.addons.webex.models import WebexMeeting

def upgrade():
    print("Creating webex_meetings table...")
    Base.metadata.create_all(bind=engine, tables=[WebexMeeting.__table__])
    print("✓ webex_meetings table created successfully")

if __name__ == "__main__":
    upgrade()
