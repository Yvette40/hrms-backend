# email_service.py
"""
Email Notification Service for HRMS
Sends payroll and leave notifications to employees
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

class EmailService:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        """
        Initialize email service
        
        For Gmail:
        1. Enable 2-Step Verification
        2. Generate App Password: https://myaccount.google.com/apppasswords
        3. Use App Password instead of regular password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = os.getenv("EMAIL_SENDER", "your-email@gmail.com")
        self.sender_password = os.getenv("EMAIL_PASSWORD", "your-app-password")
        
    def send_payroll_notification(self, employee_email, employee_name, period_start, period_end, net_salary):
        """Send payroll approved notification to employee"""
        
        subject = f"Payroll Processed - {period_start} to {period_end}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .salary-box {{
                    background: white;
                    padding: 20px;
                    margin: 20px 0;
                    border-left: 4px solid #28a745;
                    border-radius: 5px;
                }}
                .salary-amount {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #28a745;
                    margin: 10px 0;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Payroll Processed</h1>
                    <p>Glimmer Limited</p>
                </div>
                
                <div class="content">
                    <p>Dear {employee_name},</p>
                    
                    <p>Your payroll for the period <strong>{period_start}</strong> to <strong>{period_end}</strong> has been successfully processed and approved.</p>
                    
                    <div class="salary-box">
                        <p style="margin: 0; color: #666;">Net Salary</p>
                        <div class="salary-amount">KES {net_salary:,.2f}</div>
                        <p style="margin: 0; color: #666; font-size: 12px;">Payment will be processed shortly</p>
                    </div>
                    
                    <p>You can view your detailed payslip by logging into the HRMS portal:</p>
                    
                    <a href="http://localhost:3000/employee-portal" class="button">View Payslip</a>
                    
                    <p style="margin-top: 30px; font-size: 14px; color: #666;">
                        <strong>Important Notes:</strong><br>
                        • Your payslip includes details of all earnings and deductions<br>
                        • Please download and save your payslip for your records<br>
                        • Contact HR if you have any questions
                    </p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from Glimmer Limited HRMS</p>
                    <p>© {datetime.now().year} Glimmer Limited. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(employee_email, subject, html_body)
    
    def send_bulk_payroll_notifications(self, employee_list):
        """Send notifications to multiple employees"""
        results = {
            'success': [],
            'failed': []
        }
        
        for employee in employee_list:
            try:
                success = self.send_payroll_notification(
                    employee['email'],
                    employee['name'],
                    employee['period_start'],
                    employee['period_end'],
                    employee['net_salary']
                )
                
                if success:
                    results['success'].append(employee['name'])
                else:
                    results['failed'].append(employee['name'])
            except Exception as e:
                print(f"Failed to send email to {employee['name']}: {e}")
                results['failed'].append(employee['name'])
        
        return results
    
    def send_leave_approval_notification(self, employee_email, employee_name, leave_type, start_date, end_date, days):
        """Send email when leave is approved"""
        
        subject = f"✅ Leave Request Approved - {leave_type}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .leave-box {{
                    background: #d4edda;
                    padding: 20px;
                    margin: 20px 0;
                    border-left: 4px solid #28a745;
                    border-radius: 5px;
                }}
                .leave-box p {{
                    margin: 8px 0;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #27ae60;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Leave Approved!</h1>
                    <p>Glimmer Limited</p>
                </div>
                
                <div class="content">
                    <p>Dear {employee_name},</p>
                    
                    <p>Great news! Your leave request has been <strong>approved</strong>.</p>
                    
                    <div class="leave-box">
                        <p><strong>Leave Type:</strong> {leave_type}</p>
                        <p><strong>Start Date:</strong> {start_date}</p>
                        <p><strong>End Date:</strong> {end_date}</p>
                        <p><strong>Duration:</strong> {days} days</p>
                    </div>
                    
                    <p>Enjoy your time off! We look forward to seeing you back at work.</p>
                    
                    <a href="http://localhost:3000/leave" class="button">View Leave Details</a>
                    
                    <p style="margin-top: 30px; font-size: 14px; color: #666;">
                        <strong>Reminder:</strong><br>
                        • Ensure all pending work is completed or delegated<br>
                        • Update your out-of-office message<br>
                        • Have a great time!
                    </p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from Glimmer Limited HRMS</p>
                    <p>© {datetime.now().year} Glimmer Limited. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(employee_email, subject, html_body)
    
    def send_leave_rejection_notification(self, employee_email, employee_name, leave_type, start_date, end_date, reason):
        """Send email when leave is rejected"""
        
        subject = f"❌ Leave Request Declined - {leave_type}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .leave-box {{
                    background: #f8d7da;
                    padding: 20px;
                    margin: 20px 0;
                    border-left: 4px solid #e74c3c;
                    border-radius: 5px;
                }}
                .leave-box p {{
                    margin: 8px 0;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❌ Leave Request Declined</h1>
                    <p>Glimmer Limited</p>
                </div>
                
                <div class="content">
                    <p>Dear {employee_name},</p>
                    
                    <p>We regret to inform you that your leave request has been <strong>declined</strong>.</p>
                    
                    <div class="leave-box">
                        <p><strong>Leave Type:</strong> {leave_type}</p>
                        <p><strong>Start Date:</strong> {start_date}</p>
                        <p><strong>End Date:</strong> {end_date}</p>
                        <p><strong>Reason for Decline:</strong> {reason}</p>
                    </div>
                    
                    <p>If you have any questions or would like to discuss this further, please contact HR.</p>
                    
                    <a href="http://localhost:3000/leave" class="button">View Leave Status</a>
                    
                    <p style="margin-top: 30px; font-size: 14px; color: #666;">
                        <strong>Next Steps:</strong><br>
                        • You may submit a new request for different dates<br>
                        • Contact HR for clarification<br>
                        • Check your leave balance
                    </p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from Glimmer Limited HRMS</p>
                    <p>© {datetime.now().year} Glimmer Limited. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(employee_email, subject, html_body)
    
    def _send_email(self, to_email, subject, html_body):
        """Internal method to send email"""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = self.sender_email
            message['To'] = to_email
            message['Subject'] = subject
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print(f"✅ Email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {e}")
            return False