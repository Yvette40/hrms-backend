# sms_service.py
"""
SMS Notification Service for HRMS
Sends payroll notifications via SMS using Africa's Talking API
Perfect for Kenyan phone numbers
"""

import os
import africastalking
from datetime import datetime

class SMSService:
    def __init__(self):
        """
        Initialize Africa's Talking SMS service
        
        Setup:
        1. Sign up at https://africastalking.com/
        2. Get your API Key and Username from dashboard
        3. Add sandbox app or go live for production
        """
        self.username = os.getenv("AT_USERNAME", "sandbox")  # Your Africa's Talking username
        self.api_key = os.getenv("AT_API_KEY", "your-api-key-here")
        
        # Initialize SDK
        africastalking.initialize(self.username, self.api_key)
        self.sms = africastalking.SMS
    
    def send_payroll_notification(self, phone_number, employee_name, period_start, period_end, net_salary):
        """
        Send payroll notification SMS
        
        Args:
            phone_number: Format +254XXXXXXXXX (Kenyan format)
            employee_name: Employee's name
            period_start: Period start date
            period_end: Period end date
            net_salary: Net salary amount
        """
        
        # Format message (160 chars for single SMS, 306 for concatenated)
        message = (
            f"Hello {employee_name}, "
            f"Your payroll for {period_start} to {period_end} has been processed. "
            f"Net Salary: KES {net_salary:,.2f}. "
            f"Login to HRMS to view details."
        )
        
        try:
            # Send SMS
            response = self.sms.send(message, [phone_number])
            
            print(f"✅ SMS sent to {phone_number}")
            print(f"Response: {response}")
            
            return {
                'success': True,
                'response': response,
                'message': message
            }
            
        except Exception as e:
            print(f"❌ Failed to send SMS to {phone_number}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_bulk_sms(self, recipients):
        """
        Send SMS to multiple employees
        
        Args:
            recipients: List of dicts with phone_number, employee_name, period_start, period_end, net_salary
        """
        results = {
            'success': [],
            'failed': []
        }
        
        for recipient in recipients:
            result = self.send_payroll_notification(
                phone_number=recipient['phone_number'],
                employee_name=recipient['employee_name'],
                period_start=recipient['period_start'],
                period_end=recipient['period_end'],
                net_salary=recipient['net_salary']
            )
            
            if result['success']:
                results['success'].append(recipient['employee_name'])
            else:
                results['failed'].append(recipient['employee_name'])
        
        return results
    
    def send_custom_sms(self, phone_number, message):
        """Send custom SMS message"""
        try:
            response = self.sms.send(message, [phone_number])
            return {'success': True, 'response': response}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_payroll_reminder(self, phone_number, employee_name, days_until_payday):
        """Send reminder before payday"""
        message = (
            f"Hi {employee_name}, "
            f"Reminder: Payday is in {days_until_payday} days. "
            f"Glimmer Limited HRMS"
        )
        return self.send_custom_sms(phone_number, message)
    
    def get_balance(self):
        """Check SMS balance"""
        try:
            application = africastalking.Application
            balance = application.fetch_application_data()
            return balance
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return None


# ===================================================
# ALTERNATIVE: Twilio SMS Service (International)
# ===================================================

class TwilioSMSService:
    """
    Alternative SMS service using Twilio
    Good for international numbers or if Africa's Talking is not available
    """
    def __init__(self):
        """
        Initialize Twilio
        Get credentials from: https://www.twilio.com/console
        """
        from twilio.rest import Client
        
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "your-account-sid")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "your-auth-token")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")
        
        self.client = Client(self.account_sid, self.auth_token)
    
    def send_payroll_notification(self, phone_number, employee_name, period_start, period_end, net_salary):
        """Send SMS via Twilio"""
        message = (
            f"Hello {employee_name}, "
            f"Your payroll for {period_start} to {period_end} has been processed. "
            f"Net Salary: KES {net_salary:,.2f}. "
            f"Login to HRMS portal."
        )
        
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=phone_number
            )
            
            print(f"✅ SMS sent via Twilio to {phone_number}")
            return {'success': True, 'sid': message.sid}
            
        except Exception as e:
            print(f"❌ Twilio SMS failed: {e}")
            return {'success': False, 'error': str(e)}


# ===================================================
# ADD TO app.py - SMS Endpoints
# ===================================================

"""
# Add these imports at the top of app.py
from sms_service import SMSService

# Initialize SMS service
sms_service = SMSService()

@app.route("/payroll/notify-sms/<int:payroll_id>", methods=["POST"])
@jwt_required()
def send_payroll_sms(payroll_id):
    '''Send SMS notification after payroll approval'''
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can send SMS notifications"}), 403
    
    payroll = Payroll.query.get_or_404(payroll_id)
    employee = Employee.query.get(payroll.employee_id)
    
    # Check if employee has phone number
    phone_number = getattr(employee, 'phone_number', None)
    
    if not phone_number:
        return jsonify({"msg": "Employee phone number not found"}), 400
    
    # Send SMS
    result = sms_service.send_payroll_notification(
        phone_number=phone_number,
        employee_name=employee.name,
        period_start=payroll.period_start.strftime('%Y-%m-%d'),
        period_end=payroll.period_end.strftime('%Y-%m-%d'),
        net_salary=payroll.net_salary
    )
    
    # Log the action
    log_audit_action_safe(
        db,
        action_type="SMS_SENT",
        description=f"SMS notification sent to {employee.name}",
        module="NOTIFICATION",
        user_id=user.id,
        ip_address=request.remote_addr
    )
    
    if result['success']:
        return jsonify({
            "msg": "SMS sent successfully",
            "employee": employee.name,
            "phone": phone_number
        }), 200
    else:
        return jsonify({
            "msg": "Failed to send SMS",
            "error": result.get('error')
        }), 500


@app.route("/payroll/notify-sms-bulk/<int:payroll_batch_id>", methods=["POST"])
@jwt_required()
def send_bulk_sms(payroll_batch_id):
    '''Send SMS to all employees in payroll batch'''
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can send bulk SMS"}), 403
    
    # Get first payroll to find the period
    first_payroll = Payroll.query.get_or_404(payroll_batch_id)
    
    # Get all approved payrolls for this period
    payrolls = Payroll.query.filter(
        Payroll.period_start == first_payroll.period_start,
        Payroll.period_end == first_payroll.period_end,
        Payroll.status == 'Approved'
    ).all()
    
    recipients = []
    for p in payrolls:
        emp = Employee.query.get(p.employee_id)
        if hasattr(emp, 'phone_number') and emp.phone_number:
            recipients.append({
                'phone_number': emp.phone_number,
                'employee_name': emp.name,
                'period_start': p.period_start.strftime('%Y-%m-%d'),
                'period_end': p.period_end.strftime('%Y-%m-%d'),
                'net_salary': p.net_salary
            })
    
    if not recipients:
        return jsonify({"msg": "No employees with phone numbers found"}), 400
    
    # Send bulk SMS
    results = sms_service.send_bulk_sms(recipients)
    
    # Log the action
    log_audit_action_safe(
        db,
        action_type="BULK_SMS_SENT",
        description=f"Bulk SMS sent to {len(results['success'])} employees",
        module="NOTIFICATION",
        user_id=user.id,
        ip_address=request.remote_addr
    )
    
    return jsonify({
        "msg": "Bulk SMS completed",
        "success": len(results['success']),
        "failed": len(results['failed']),
        "details": results
    }), 200


@app.route("/sms/check-balance", methods=["GET"])
@jwt_required()
def check_sms_balance():
    '''Check SMS balance (Admin only)'''
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if user.role != 'Admin':
        return jsonify({"msg": "Only Admin can check balance"}), 403
    
    balance = sms_service.get_balance()
    
    return jsonify({
        "balance": balance
    }), 200
"""
