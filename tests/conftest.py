import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://user:pass@localhost/user_db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
