
import random
from datetime import datetime, timedelta

# Kenyan first names (mix of ethnic backgrounds)
FIRST_NAMES_MALE = [
    "John", "James", "Peter", "David", "Michael", "Joseph", "Daniel", "Samuel", 
    "Patrick", "Robert", "Stephen", "Paul", "Brian", "Kevin", "Eric", "Victor",
    "Felix", "Dennis", "Anthony", "George", "Francis", "Martin", "Simon", "Mark",
    "Charles", "Emmanuel", "Vincent", "Nicholas", "Andrew", "Philip", "Timothy",
    "Edwin", "Kenneth", "Collins", "Ian", "Alex", "Allan", "Moses", "Joshua"
]

FIRST_NAMES_FEMALE = [
    "Mary", "Jane", "Grace", "Lucy", "Ann", "Rose", "Susan", "Catherine",
    "Margaret", "Joyce", "Faith", "Rachel", "Elizabeth", "Sarah", "Rebecca",
    "Nancy", "Betty", "Esther", "Ruth", "Hannah", "Mercy", "Lydia", "Joan",
    "Agnes", "Beatrice", "Christine", "Monica", "Caroline", "Alice", "Eunice",
    "Josephine", "Patricia", "Jennifer", "Michelle", "Sharon", "Cynthia"
]

# Kenyan surnames (representing diverse ethnic backgrounds)
SURNAMES = [
    # Kikuyu
    "Mwangi", "Kamau", "Njoroge", "Kariuki", "Wanjiru", "Wambui", "Nyambura",
    "Muthoni", "Njeri", "Waithera", "Karanja", "Kimani", "Githinji", "Kinyanjui",
    
    # Luo
    "Ochieng", "Otieno", "Omondi", "Owino", "Akinyi", "Adhiambo", "Awino",
    "Onyango", "Odhiambo", "Okoth", "Odongo", "Ouma", "Obiero",
    
    # Luhya
    "Wanjala", "Wafula", "Barasa", "Wekesa", "Shikuku", "Mukhwana", "Khaemba",
    "Makokha", "Simiyu", "Muliro", "Waswa",
    
    # Kalenjin
    "Kipchoge", "Chebet", "Ruto", "Koech", "Bett", "Rotich", "Keter", "Sang",
    "Kirui", "Kibet", "Lagat", "Chepkwony",
    
    # Kamba
    "Mutua", "Mwikali", "Musyoka", "Mumo", "Ndunge", "Kyalo", "Kilonzo",
    "Mwende", "Nduku", "Kioko",
    
    # Kisii
    "Nyaboke", "Ombati", "Nyamongo", "Ondieki", "Mong'are", "Bosire",
    
    # Meru/Embu
    "Mwirigi", "Gatwiri", "Kagwiria", "M'maitai", "Nkirote",
    
    # Coastal
    "Mohamed", "Hassan", "Ali", "Abdalla", "Omar", "Salim", "Hamisi"
]

# Departments and their positions
DEPARTMENTS = {
    "Engineering": {
        "positions": [
            ("Software Engineer", 50000, 80000),
            ("Senior Software Engineer", 80000, 120000),
            ("Lead Developer", 100000, 150000),
            ("DevOps Engineer", 70000, 110000),
            ("QA Engineer", 45000, 75000),
            ("System Architect", 120000, 180000),
            ("Junior Developer", 35000, 55000),
        ],
        "count": 12
    },
    "Finance": {
        "positions": [
            ("Accountant", 45000, 70000),
            ("Senior Accountant", 70000, 100000),
            ("Financial Analyst", 50000, 80000),
            ("Finance Manager", 90000, 140000),
            ("Accounts Assistant", 35000, 50000),
            ("Auditor", 55000, 85000),
        ],
        "count": 8
    },
    "Sales": {
        "positions": [
            ("Sales Executive", 40000, 65000),
            ("Sales Manager", 70000, 110000),
            ("Business Development Manager", 80000, 130000),
            ("Sales Representative", 35000, 55000),
            ("Key Account Manager", 65000, 95000),
        ],
        "count": 10
    },
    "Marketing": {
        "positions": [
            ("Marketing Officer", 45000, 70000),
            ("Marketing Manager", 75000, 115000),
            ("Digital Marketing Specialist", 50000, 80000),
            ("Content Creator", 40000, 60000),
            ("Brand Manager", 70000, 105000),
        ],
        "count": 7
    },
    "HR": {
        "positions": [
            ("HR Assistant", 38000, 55000),
            ("HR Officer", 50000, 75000),
            ("HR Manager", 80000, 120000),
            ("Recruitment Specialist", 45000, 70000),
            ("Training Officer", 48000, 72000),
        ],
        "count": 6
    },
    "Operations": {
        "positions": [
            ("Operations Manager", 75000, 115000),
            ("Operations Coordinator", 45000, 68000),
            ("Project Manager", 70000, 110000),
            ("Logistics Officer", 42000, 65000),
        ],
        "count": 7
    },
    "IT": {
        "positions": [
            ("IT Support Specialist", 40000, 65000),
            ("Network Administrator", 55000, 85000),
            ("IT Manager", 85000, 130000),
            ("Database Administrator", 65000, 100000),
            ("Help Desk Officer", 35000, 50000),
        ],
        "count": 6
    },
    "Customer Service": {
        "positions": [
            ("Customer Service Representative", 32000, 48000),
            ("Customer Service Manager", 60000, 90000),
            ("Support Specialist", 38000, 58000),
        ],
        "count": 8
    },
    "Legal": {
        "positions": [
            ("Legal Officer", 60000, 95000),
            ("Legal Counsel", 90000, 140000),
            ("Compliance Officer", 55000, 85000),
        ],
        "count": 4
    },
    "Procurement": {
        "positions": [
            ("Procurement Officer", 48000, 72000),
            ("Procurement Manager", 75000, 115000),
            ("Supply Chain Analyst", 52000, 78000),
        ],
        "count": 5
    },
    "Admin": {
        "positions": [
            ("Office Administrator", 38000, 58000),
            ("Administrative Assistant", 32000, 48000),
            ("Office Manager", 55000, 85000),
        ],
        "count": 6
    },
    "Logistics": {
        "positions": [
            ("Logistics Coordinator", 45000, 68000),
            ("Transport Manager", 60000, 90000),
            ("Warehouse Supervisor", 42000, 63000),
        ],
        "count": 5
    }
}

def generate_national_id():
    """Generate a realistic Kenyan National ID number (8 digits)"""
    return str(random.randint(10000000, 99999999))

def generate_phone():
    """Generate a realistic Kenyan phone number"""
    prefixes = ['712', '713', '714', '715', '722', '723', '724', '725', '733', '734', '740', '741', '742', '743', '745', '746', '757', '758', '759', '768', '769']
    return f"+254{random.choice(prefixes)}{random.randint(100000, 999999)}"

def generate_email(first_name, surname, domain="glimmer.com"):
    """Generate company email"""
    return f"{first_name.lower()}.{surname.lower()}@{domain}"

def generate_username(first_name, surname):
    """Generate username (first letter + surname)"""
    return f"{first_name[0].lower()}{surname.lower()}"

def generate_join_date():
    """Generate a join date within the last 5 years"""
    days_ago = random.randint(30, 1825)  # 30 days to 5 years
    return (datetime.now() - timedelta(days=days_ago)).date()

def generate_employees_data():
    """Generate comprehensive employee data"""
    employees_data = []
    used_national_ids = set()
    used_usernames = set()
    
    for dept_name, dept_info in DEPARTMENTS.items():
        positions = dept_info["positions"]
        count = dept_info["count"]
        
        for i in range(count):
            # Randomly select gender
            is_male = random.choice([True, False])
            first_name = random.choice(FIRST_NAMES_MALE if is_male else FIRST_NAMES_FEMALE)
            surname = random.choice(SURNAMES)
            
            # Ensure unique national ID
            while True:
                national_id = generate_national_id()
                if national_id not in used_national_ids:
                    used_national_ids.add(national_id)
                    break
            
            # Ensure unique username
            base_username = generate_username(first_name, surname)
            username = base_username
            counter = 1
            while username in used_usernames:
                username = f"{base_username}{counter}"
                counter += 1
            used_usernames.add(username)
            
            # Select position and salary
            position_info = random.choice(positions)
            position = position_info[0]
            min_salary = position_info[1]
            max_salary = position_info[2]
            base_salary = random.randint(min_salary, max_salary)
            
            # Round salary to nearest 1000
            base_salary = round(base_salary / 1000) * 1000
            
            employee = {
                "name": f"{first_name} {surname}",
                "national_id": national_id,
                "base_salary": base_salary,
                "phone_number": generate_phone(),
                "email": generate_email(first_name, surname),
                "department": dept_name,
                "position": position,
                "username": username,
                "password": "password123",  # Default password for all
                "join_date": generate_join_date().isoformat()
            }
            
            employees_data.append(employee)
    
    return employees_data

def print_employees_summary(employees):
    """Print a summary of generated employees"""
    print(f"\n{'='*80}")
    print(f"Generated {len(employees)} Employees")
    print(f"{'='*80}\n")
    
    # Group by department
    dept_counts = {}
    for emp in employees:
        dept = emp["department"]
        if dept not in dept_counts:
            dept_counts[dept] = []
        dept_counts[dept].append(emp)
    
    for dept, emps in sorted(dept_counts.items()):
        print(f"\n{dept} ({len(emps)} employees):")
        print("-" * 80)
        for emp in sorted(emps, key=lambda x: x["name"]):
            print(f"  {emp['name']:30} | {emp['position']:35} | KES {emp['base_salary']:,}")
    
    print(f"\n{'='*80}")
    print(f"Salary Statistics:")
    print(f"{'='*80}")
    salaries = [emp['base_salary'] for emp in employees]
    print(f"  Minimum Salary: KES {min(salaries):,}")
    print(f"  Maximum Salary: KES {max(salaries):,}")
    print(f"  Average Salary: KES {sum(salaries) // len(salaries):,}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    employees = generate_employees_data()
    print_employees_summary(employees)
    
    # Export to JSON for easy use
    import json
    with open('employees_data.json', 'w') as f:
        json.dump(employees, f, indent=2)
    print("✅ Data exported to employees_data.json")