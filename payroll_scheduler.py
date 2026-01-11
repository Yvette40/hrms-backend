# payroll_scheduler.py
"""
Payroll Scheduler Service
Automatically runs payroll on scheduled dates
FIXED VERSION - No circular imports
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PayrollScheduler:
    def __init__(self, app=None, db=None):
        """Initialize the scheduler"""
        self.scheduler = BackgroundScheduler()
        self.app = app
        self.db = db
        self.sms_service = None
        
    def init_app(self, app, db, sms_service):
        """Initialize with Flask app context"""
        self.app = app
        self.db = db
        self.sms_service = sms_service
        
    def calculate_payroll_for_employee(self, employee, period_start, period_end):
        """Calculate payroll for one employee"""
        from models import Attendance
        
        # Get attendance days
        attendance_days = Attendance.query.filter(
            Attendance.employee_id == employee.id,
            Attendance.date >= period_start,
            Attendance.date <= period_end,
            Attendance.status == "Present"
        ).count()
        
        # Basic salary
        gross_salary = float(employee.base_salary)
        
        # Calculate deductions (Kenyan tax system)
        nssf = min(gross_salary * 0.06, 1080)
        
        # NHIF based on salary brackets
        if gross_salary <= 5999:
            nhif = 150
        elif gross_salary <= 7999:
            nhif = 300
        elif gross_salary <= 11999:
            nhif = 400
        elif gross_salary <= 14999:
            nhif = 500
        elif gross_salary <= 19999:
            nhif = 600
        elif gross_salary <= 24999:
            nhif = 750
        elif gross_salary <= 29999:
            nhif = 850
        elif gross_salary <= 34999:
            nhif = 900
        elif gross_salary <= 39999:
            nhif = 950
        elif gross_salary <= 44999:
            nhif = 1000
        elif gross_salary <= 49999:
            nhif = 1100
        elif gross_salary <= 59999:
            nhif = 1200
        elif gross_salary <= 69999:
            nhif = 1300
        elif gross_salary <= 79999:
            nhif = 1400
        elif gross_salary <= 89999:
            nhif = 1500
        elif gross_salary <= 99999:
            nhif = 1600
        else:
            nhif = 1700
        
        # PAYE calculation
        taxable_income = gross_salary - nssf
        if taxable_income <= 24000:
            paye = taxable_income * 0.10
        elif taxable_income <= 32333:
            paye = 2400 + (taxable_income - 24000) * 0.25
        else:
            paye = 4483.25 + (taxable_income - 32333) * 0.30
        
        personal_relief = 2400
        paye = max(paye - personal_relief, 0)
        
        # Housing levy
        housing_levy = gross_salary * 0.015
        
        # Total deductions
        total_deductions = nssf + nhif + paye + housing_levy
        
        # Net salary
        net_salary = gross_salary - total_deductions
        
        # Anomaly detection
        anomaly_flag = attendance_days == 0
        
        return {
            'employee_id': employee.id,
            'gross_salary': gross_salary,
            'nssf': nssf,
            'nhif': nhif,
            'paye': paye,
            'housing_levy': housing_levy,
            'total_deductions': total_deductions,
            'net_salary': net_salary,
            'attendance_days': attendance_days,
            'anomaly_flag': anomaly_flag
        }
    
    def run_monthly_payroll(self):
        """
        Automatically run monthly payroll
        Called on the last day of each month
        """
        logger.info("🔄 Starting automatic monthly payroll...")
        
        with self.app.app_context():
            try:
                from models import Employee, Payroll, User
                
                # Calculate period (last month)
                today = datetime.now().date()
                period_end = today.replace(day=1) - timedelta(days=1)  # Last day of previous month
                period_start = period_end.replace(day=1)  # First day of previous month
                
                # Check if payroll already exists
                existing = Payroll.query.filter(
                    Payroll.period_start == period_start,
                    Payroll.period_end == period_end
                ).first()
                
                if existing:
                    logger.info(f"⚠️ Payroll already exists for {period_start} to {period_end}")
                    return
                
                # Get all active employees
                employees = Employee.query.filter_by(active=True).all()
                
                if not employees:
                    logger.warning("⚠️ No active employees found")
                    return
                
                # Get system user (for prepared_by)
                system_user = User.query.filter_by(username='admin').first()
                if not system_user:
                    logger.error("❌ System user not found")
                    return
                
                payroll_records = []
                sms_recipients = []
                
                # Calculate payroll for each employee
                for emp in employees:
                    calc = self.calculate_payroll_for_employee(emp, period_start, period_end)
                    
                    payroll = Payroll(
                        employee_id=emp.id,
                        period_start=period_start,
                        period_end=period_end,
                        gross_salary=calc['gross_salary'],
                        nssf=calc['nssf'],
                        nhif=calc['nhif'],
                        paye=calc['paye'],
                        housing_levy=calc['housing_levy'],
                        total_deductions=calc['total_deductions'],
                        net_salary=calc['net_salary'],
                        attendance_days=calc['attendance_days'],
                        anomaly_flag=calc['anomaly_flag'],
                        status='Approved',  # Auto-approved for scheduled payroll
                        prepared_by=system_user.id,
                        approved_by=system_user.id,
                        approved_at=datetime.utcnow()
                    )
                    
                    self.db.session.add(payroll)
                    payroll_records.append(payroll)
                    
                    # Prepare SMS notification
                    if hasattr(emp, 'phone_number') and emp.phone_number:
                        sms_recipients.append({
                            'phone_number': emp.phone_number,
                            'employee_name': emp.name,
                            'period_start': period_start.strftime('%Y-%m-%d'),
                            'period_end': period_end.strftime('%Y-%m-%d'),
                            'net_salary': calc['net_salary']
                        })
                
                self.db.session.commit()
                
                logger.info(f"✅ Payroll created for {len(payroll_records)} employees")
                
                # Send SMS notifications
                if sms_recipients and self.sms_service:
                    logger.info(f"📱 Sending SMS to {len(sms_recipients)} employees...")
                    results = self.sms_service.send_bulk_sms(sms_recipients)
                    logger.info(f"✅ SMS sent: {len(results['success'])} success, {len(results['failed'])} failed")
                
                logger.info("✅ Automatic payroll completed successfully!")
                
            except Exception as e:
                logger.error(f"❌ Error in automatic payroll: {e}")
                import traceback
                traceback.print_exc()
    
    def send_payday_reminders(self):
        """
        Send reminders 3 days before payday
        """
        logger.info("📱 Sending payday reminders...")
        
        with self.app.app_context():
            try:
                from models import Employee
                
                employees = Employee.query.filter_by(active=True).all()
                
                if not self.sms_service:
                    logger.warning("⚠️ SMS service not initialized")
                    return
                
                for emp in employees:
                    if hasattr(emp, 'phone_number') and emp.phone_number:
                        self.sms_service.send_payroll_reminder(
                            phone_number=emp.phone_number,
                            employee_name=emp.name,
                            days_until_payday=3
                        )
                
                logger.info(f"✅ Reminders sent to {len(employees)} employees")
                
            except Exception as e:
                logger.error(f"❌ Error sending reminders: {e}")
    
    def start(self):
        """Start the scheduler with all jobs"""
        
        # Job 1: Run payroll on last day of month at 11:59 PM
        self.scheduler.add_job(
            func=self.run_monthly_payroll,
            trigger=CronTrigger(day='last', hour=23, minute=59),
            id='monthly_payroll',
            name='Monthly Payroll Processing',
            replace_existing=True
        )
        
        # Job 2: Send payday reminders on 28th of each month at 9 AM
        self.scheduler.add_job(
            func=self.send_payday_reminders,
            trigger=CronTrigger(day=28, hour=9, minute=0),
            id='payday_reminders',
            name='Payday Reminders',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("✅ Payroll scheduler started successfully!")
        logger.info("📅 Scheduled jobs:")
        for job in self.scheduler.get_jobs():
            logger.info(f"  - {job.name}: {job.next_run_time}")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("⏹️ Payroll scheduler stopped")
    
    def list_jobs(self):
        """List all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': str(job.next_run_time),
                'trigger': str(job.trigger)
            })
        return jobs
    
    def run_job_now(self, job_id):
        """Manually trigger a scheduled job"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.modify(next_run_time=datetime.now())
                logger.info(f"✅ Job '{job_id}' will run immediately")
                return True
            else:
                logger.error(f"❌ Job '{job_id}' not found")
                return False
        except Exception as e:
            logger.error(f"❌ Error running job: {e}")
            return False