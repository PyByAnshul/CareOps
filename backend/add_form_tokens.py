#!/usr/bin/env python3
"""
Migration script to add tokens to existing forms
"""
import secrets
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import get_settings

def add_form_tokens():
    """Add tokens to existing forms that don't have them."""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # First, add the token column if it doesn't exist (without UNIQUE constraint)
        try:
            conn.execute(text("ALTER TABLE forms ADD COLUMN token VARCHAR"))
            conn.commit()
            print("Added token column to forms table")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("Token column already exists")
            else:
                print(f"Error adding token column: {e}")
                return
        
        # Get all forms without tokens
        result = conn.execute(text("SELECT id FROM forms WHERE token IS NULL OR token = ''"))
        forms_without_tokens = result.fetchall()
        
        print(f"Found {len(forms_without_tokens)} forms without tokens")
        
        # Add tokens to forms that don't have them
        for form in forms_without_tokens:
            form_id = form[0]
            token = secrets.token_urlsafe(32)
            
            try:
                conn.execute(
                    text("UPDATE forms SET token = :token WHERE id = :form_id"),
                    {"token": token, "form_id": form_id}
                )
                print(f"Added token to form {form_id}")
            except Exception as e:
                print(f"Error adding token to form {form_id}: {e}")
        
        # Now try to add the unique constraint (SQLite doesn't support this directly)
        # We'll create an index instead
        try:
            conn.execute(text("CREATE UNIQUE INDEX idx_forms_token ON forms(token)"))
            conn.commit()
            print("Added unique index on token column")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("Unique index on token already exists")
            else:
                print(f"Warning: Could not add unique constraint: {e}")
        
        conn.commit()
        print("Migration completed successfully")

if __name__ == "__main__":
    add_form_tokens()