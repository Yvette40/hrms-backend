# ==============================================================================
# FILE: backend/utils/sod_checker.py (NEW FILE)
# PURPOSE: Separation of Duties validation logic
# ==============================================================================

from flask import jsonify
from utils.audit_logger import log_sod_check

class SeparationOfDutiesViolation(Exception):
    """Custom exception for SOD violations"""
    pass


def check_payroll_separation(db, payroll_id, approver_id):
    """
    Rule: User who prepared payroll cannot approve it
    
    Args:
        db: Database session
        payroll_id: ID of payroll being approved
        approver_id: ID of user trying to approve
        
    Returns:
        True if allowed, raises SeparationOfDutiesViolation if blocked
    """
    from models import Payroll
    
    payroll = Payroll.query.get(payroll_id)
    if not payroll:
        return True
    
    if payroll.prepared_by == approver_id:
        # Log the violation
        log_sod_check(
            db=db,
            rule_name="Payroll Approval Separation",
            user_id=approver_id,
            status="BLOCKED",
            action_attempted=f"Approve payroll #{payroll_id}",
            details=f"User {approver_id} tried to approve payroll they prepared"
        )
        
        raise SeparationOfDutiesViolation(
            "Separation of Duties Violation: You cannot approve payroll you prepared."
        )
    
    # Log that check passed
    log_sod_check(
        db=db,
        rule_name="Payroll Approval Separation",
        user_id=approver_id,
        status="ALLOWED",
        action_attempted=f"Approve payroll #{payroll_id}",
        details=f"Different user approving payroll"
    )
    
    return True


def check_employee_modification_separation(db, employee_id, modifier_id, creator_id):
    """
    Rule: Significant employee changes should be reviewed by different person
    
    Args:
        db: Database session
        employee_id: ID of employee being modified
        modifier_id: ID of user making changes
        creator_id: ID of user who created employee
        
    Returns:
        True (allowed), or logs WARNING if same person
    """
    if creator_id == modifier_id:
        log_sod_check(
            db=db,
            rule_name="Employee Modification Review",
            user_id=modifier_id,
            status="WARNING",
            action_attempted=f"Modify employee #{employee_id}",
            details=f"Same user modifying employee they created"
        )
        # Don't block, just warn
    else:
        log_sod_check(
            db=db,
            rule_name="Employee Modification Review",
            user_id=modifier_id,
            status="ALLOWED",
            action_attempted=f"Modify employee #{employee_id}",
            details="Different user modifying employee"
        )
    
    return True


def check_approval_request_separation(db, request_id, reviewer_id):
    """
    Rule: User cannot approve their own request
    
    Args:
        db: Database session
        request_id: ID of approval request
        reviewer_id: ID of user trying to review
        
    Returns:
        True if allowed, raises SeparationOfDutiesViolation if blocked
    """
    from models import ApprovalRequest
    
    request = ApprovalRequest.query.get(request_id)
    if not request:
        return True
    
    if request.requested_by == reviewer_id:
        log_sod_check(
            db=db,
            rule_name="Self-Approval Prevention",
            user_id=reviewer_id,
            status="BLOCKED",
            action_attempted=f"Approve request #{request_id}",
            details=f"User tried to approve their own request"
        )
        
        raise SeparationOfDutiesViolation(
            "Separation of Duties Violation: You cannot approve your own request."
        )
    
    log_sod_check(
        db=db,
        rule_name="Self-Approval Prevention",
        user_id=reviewer_id,
        status="ALLOWED",
        action_attempted=f"Approve request #{request_id}",
        details="Different user reviewing request"
    )
    
    return True