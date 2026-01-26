from app import app, db
from sqlalchemy import text

with app.app_context():
    # Rename column from nhif to sha
    try:
        db.session.execute(text('ALTER TABLE payroll RENAME COLUMN nhif TO sha'))
        db.session.commit()
        print('✅ Database column renamed: nhif → sha')
    except Exception as e:
        print(f'❌ Error: {e}')
        print('Column might already be renamed or error occurred')
