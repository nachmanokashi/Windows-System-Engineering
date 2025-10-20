import os
import sys

# הגדרת נתיבים על מנת לאפשר ייבוא מ-app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from app.core.db import SessionLocal
from app.core.auth_utils import get_password_hash
from app.mvc.models.users.user_entity import User

# ============================================
# הגדרות משתמש
# ============================================
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@example.com"  
ADMIN_PASSWORD = "admin123"
ADMIN_FULL_NAME = "System Administrator"

def create_admin_user():
    """יוצר משתמש אדמין חדש במסד הנתונים"""
    
    # ודא שהסיסמה שונתה מברירת המחדל
    if ADMIN_PASSWORD == "YOUR_ADMIN_PASSWORD":
        print("🛑 ERROR: Please change ADMIN_PASSWORD in the script before running.")
        return

    db = SessionLocal()
    try:
        # 1. בדוק אם המשתמש כבר קיים
        existing_user = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        if existing_user:
            print(f"✅ User '{ADMIN_USERNAME}' already exists.")
            # ודא שהוא אדמין
            if not existing_user.is_admin:
                existing_user.is_admin = True
                db.commit()
                print(f"   Updated user '{ADMIN_USERNAME}' to be an Admin.")
            return

        # 2. יצירת hash לסיסמה
        # הפונקציה get_password_hash משתמשת ב-bcrypt
        hashed_password = get_password_hash(ADMIN_PASSWORD)

        # 3. יצירת האובייקט
        admin_user = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            hashed_password=hashed_password,
            full_name=ADMIN_FULL_NAME,
            is_active=True,
            is_admin=True  
        )

        # 4. שמירה במסד הנתונים
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("-" * 50)
        print(f"🎉 Successfully created new Admin user: {admin_user.username}")
        print(f"   ID: {admin_user.id}")
        print(f"   Email: {admin_user.email}")
        print(f"   Is Admin: {admin_user.is_admin}")
        print("-" * 50)

    except Exception as e:
        db.rollback()
        print(f"❌ Failed to create user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()