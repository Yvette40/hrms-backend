from app import app, db, Employee

with app.app_context():
    evan = Employee.query.filter_by(name='Evan Patterson').first()
    
    if evan:
        print(f'Employee: {evan.name}')
        print(f'Email: {evan.email}')
    else:
        print('Evan Patterson not found')
