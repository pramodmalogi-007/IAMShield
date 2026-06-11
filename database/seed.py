"""
IAMShield - Standalone MongoDB Seeder
Run independently to seed all collections:
  cd backend && python ../database/seed.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from models.database import seed_database, get_db

if __name__ == '__main__':
    print("IAMShield MongoDB Seeder")
    print("=" * 40)
    try:
        seed_database()
        db = get_db()
        print(f"  categories : {db.categories.count_documents({})} docs")
        print(f"  questions  : {db.questions.count_documents({})} docs")
        print(f"  products   : {db.products.count_documents({})} docs")
        print("Done.")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
