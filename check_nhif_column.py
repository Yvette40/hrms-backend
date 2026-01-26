from app import app, db, Payroll

with app.app_context():
    # Check if nhif column exists
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    columns = inspector.get_columns('payroll')
    
    print('Payroll table columns:')
    for col in columns:
        if 'nhif' in col['name'].lower() or 'sha' in col['name'].lower():
            print(f'  - {col["name"]}: {col["type"]}')
