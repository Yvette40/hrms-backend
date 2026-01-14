# scheduler_service.py - Automated Task Scheduler
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HRMSScheduler:
    def __init__(self, app, db):
        self.app = app
        self.db = db
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logger.info("📅 HRMS Scheduler started")
    
    def send_payroll_reminders(self):
        """Send reminders for pending payroll approvals"""
        with self.app.app_context():
            from models import Payroll, User, Employee
            from email_service import EmailService
            
            # Get all pending payrolls
            pending_payrolls = Payroll.query.filter_by(status='Pending').all()
            
            if not pending_payrolls:
                logger.info("No pending payrolls to remind about")
                return
            
            # Get admin users
            admins = User.query.filter_by(role='Admin').all()
            
            email_service = EmailService()
            
            for admin in admins:
                if admin.email:
                    try:
                        # Group payrolls by period
                        periods = {}
                        for p in pending_payrolls:
                            key = f"{p.period_start} - {p.period_end}"
                            if key not in periods:
                                periods[key] = 0
                            periods[key] += 1
                        
                        # Send reminder email
                        subject = "⏰ Payroll Approval Reminder"
                        body = f"""
Dear {admin.username},

This is a reminder that you have pending payroll approvals:

"""
                        for period, count in periods.items():
                            body += f"- {period}: {count} employees\n"
                        
                        body += f"""
Total pending: {len(pending_payrolls)} payrolls

Please log in to the HRMS to review and approve these payrolls.

Best regards,
Glimmer Limited HRMS
                        """
                        
                        email_service.send_email(admin.email, subject, body)
                        logger.info(f"✅ Sent reminder to {admin.username}")
                    except Exception as e:
                        logger.error(f"❌ Failed to send reminder to {admin.username}: {e}")
            
            logger.info(f"📧 Payroll reminders sent to {len(admins)} admins")
    
    def send_attendance_reminders(self):
        """Send attendance reminders to employees"""
        with self.app.app_context():
            from models import Employee, Attendance
            from email_service import EmailService
            from datetime import date
            
            today = date.today()
            
            # Get all active employees
            employees = Employee.query.filter_by(active=True).all()
            
            email_service = EmailService()
            
            for emp in employees:
                # Check if attendance already marked today
                attendance_today = Attendance.query.filter_by(
                    employee_id=emp.id,
                    date=today
                ).first()
                
                if not attendance_today and emp.email:
                    try:
                        subject = "📅 Attendance Reminder"
                        body = f"""
Dear {emp.name},

This is a reminder to mark your attendance for today ({today.strftime('%Y-%m-%d')}).

Please log in to the HRMS to mark your attendance.

Best regards,
Glimmer Limited HRMS
                        """
                        
                        email_service.send_email(emp.email, subject, body)
                        logger.info(f"✅ Sent attendance reminder to {emp.name}")
                    except Exception as e:
                        logger.error(f"❌ Failed to send attendance reminder to {emp.name}: {e}")
            
            logger.info(f"📧 Attendance reminders processed for {len(employees)} employees")
    
    def generate_monthly_reports(self):
        """Generate monthly reports automatically"""
        with self.app.app_context():
            from models import Payroll, Attendance, Employee
            from datetime import date
            import calendar
            
            today = date.today()
            # Get last month
            if today.month == 1:
                last_month = 12
                last_year = today.year - 1
            else:
                last_month = today.month - 1
                last_year = today.year
            
            # Get first and last day of last month
            first_day = date(last_year, last_month, 1)
            last_day = date(last_year, last_month, calendar.monthrange(last_year, last_month)[1])
            
            # Count stats
            payrolls = Payroll.query.filter(
                Payroll.period_start >= first_day,
                Payroll.period_end <= last_day
            ).all()
            
            total_payroll = sum(p.net_salary for p in payrolls)
            total_employees = len(set(p.employee_id for p in payrolls))
            
            logger.info(f"""
📊 Monthly Report Generated for {first_day.strftime('%B %Y')}:
   - Total Employees: {total_employees}
   - Total Payroll: KSh {total_payroll:,.2f}
   - Average Salary: KSh {total_payroll / total_employees if total_employees > 0 else 0:,.2f}
            """)
    
    def cleanup_old_sessions(self):
        """Clean up expired sessions and tokens"""
        with self.app.app_context():
            logger.info("🧹 Cleaning up old sessions...")
            # Add your cleanup logic here
            # For example, delete old audit logs older than 1 year
            from models import AuditLog
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=365)
            old_logs = AuditLog.query.filter(AuditLog.timestamp < cutoff_date).all()
            
            count = len(old_logs)
            for log in old_logs:
                self.db.session.delete(log)
            
            self.db.session.commit()
            logger.info(f"🧹 Deleted {count} old audit logs")
    
    def setup_jobs(self):
        """Setup all scheduled jobs"""
        
        # Payroll approval reminders - Every Monday at 9 AM
        self.scheduler.add_job(
            func=self.send_payroll_reminders,
            trigger='cron',
            day_of_week='mon',
            hour=9,
            minute=0,
            id='payroll_reminders',
            name='Send Payroll Approval Reminders',
            replace_existing=True
        )
        logger.info("✅ Job scheduled: Payroll reminders (Mon 9 AM)")
        
        # Attendance reminders - Every weekday at 8 AM
        self.scheduler.add_job(
            func=self.send_attendance_reminders,
            trigger='cron',
            day_of_week='mon-fri',
            hour=8,
            minute=0,
            id='attendance_reminders',
            name='Send Attendance Reminders',
            replace_existing=True
        )
        logger.info("✅ Job scheduled: Attendance reminders (Mon-Fri 8 AM)")
        
        # Monthly reports - 1st of every month at 10 AM
        self.scheduler.add_job(
            func=self.generate_monthly_reports,
            trigger='cron',
            day=1,
            hour=10,
            minute=0,
            id='monthly_reports',
            name='Generate Monthly Reports',
            replace_existing=True
        )
        logger.info("✅ Job scheduled: Monthly reports (1st of month 10 AM)")
        
        # Cleanup old data - Every Sunday at 2 AM
        self.scheduler.add_job(
            func=self.cleanup_old_sessions,
            trigger='cron',
            day_of_week='sun',
            hour=2,
            minute=0,
            id='cleanup',
            name='Cleanup Old Data',
            replace_existing=True
        )
        logger.info("✅ Job scheduled: Cleanup (Sun 2 AM)")
        
        logger.info("📅 All scheduled jobs configured!")
    
    def get_jobs(self):
        """Get list of all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else 'N/A',
                'trigger': str(job.trigger)
            })
        return jobs
    
    def run_job_now(self, job_id):
        """Manually trigger a job"""
        job = self.scheduler.get_job(job_id)
        if job:
            job.func()
            logger.info(f"✅ Manually executed job: {job_id}")
            return True
        else:
            logger.error(f"❌ Job not found: {job_id}")
            return False
    
    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        logger.info("📅 Scheduler shutdown")

# Global scheduler instance
scheduler_instance = None

def init_scheduler(app, db):
    """Initialize the scheduler"""
    global scheduler_instance
    scheduler_instance = HRMSScheduler(app, db)
    scheduler_instance.setup_jobs()
    return scheduler_instance
