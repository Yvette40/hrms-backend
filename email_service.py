# email_service.py
"""
Email Notification Service for HRMS
Sends payroll notifications to employees
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os

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


# ===================================================
# ADD TO app.py - New endpoint for sending notifications
# ===================================================

# Add this import at the top of app.py
# from email_service import EmailService

# Add this endpoint to app.py

"""
@app.route("/payroll/notify/<int:payroll_id>", methods=["POST"])
@jwt_required()
def send_payroll_notification(payroll_id):
    '''Send email notification after payroll approval'''
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can send notifications"}), 403
    
    payroll = Payroll.query.get_or_404(payroll_id)
    employee = Employee.query.get(payroll.employee_id)
    
    # TODO: Add email field to Employee model
    employee_email = getattr(employee, 'email', None)
    
    if not employee_email:
        return jsonify({"msg": "Employee email not found"}), 400
    
    email_service = EmailService()
    success = email_service.send_payroll_notification(
        employee_email=employee_email,
        employee_name=employee.name,
        period_start=payroll.period_start.strftime('%Y-%m-%d'),
        period_end=payroll.period_end.strftime('%Y-%m-%d'),
        net_salary=payroll.net_salary
    )
    
    if success:
        return jsonify({"msg": "Notification sent successfully"}), 200
    else:
        return jsonify({"msg": "Failed to send notification"}), 500


@app.route("/payroll/notify-all/<int:payroll_batch_id>", methods=["POST"])
@jwt_required()
def send_bulk_notifications(payroll_batch_id):
    '''Send notifications to all employees in a payroll batch'''
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can send notifications"}), 403
    
    # Get first payroll to find the period
    first_payroll = Payroll.query.get_or_404(payroll_batch_id)
    
    # Get all approved payrolls for this period
    payrolls = Payroll.query.filter(
        Payroll.period_start == first_payroll.period_start,
        Payroll.period_end == first_payroll.period_end,
        Payroll.status == 'Approved'
    ).all()
    
    employee_list = []
    for p in payrolls:
        emp = Employee.query.get(p.employee_id)
        if hasattr(emp, 'email') and emp.email:
            employee_list.append({
                'email': emp.email,
                'name': emp.name,
                'period_start': p.period_start.strftime('%Y-%m-%d'),
                'period_end': p.period_end.strftime('%Y-%m-%d'),
                'net_salary': p.net_salary
            })
    
    if not employee_list:
        return jsonify({"msg": "No employees with email addresses found"}), 400
    
    email_service = EmailService()
    results = email_service.send_bulk_payroll_notifications(employee_list)
    
    return jsonify({
        "msg": "Bulk notifications completed",
        "success": len(results['success']),
        "failed": len(results['failed']),
        "details": results
    }), 200
"""
