# pdf_service.py - PDF Generation Service for Payslips
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from datetime import datetime

class PayslipPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.company_name = "Glimmer Limited"
        self.company_address = "Nairobi, Kenya"
        
    def generate_payslip(self, employee_data, payroll_data):
        """
        Generate a professional payslip PDF
        
        Args:
            employee_data: dict with employee info (name, id, department, etc.)
            payroll_data: dict with payroll info (gross, deductions, net, etc.)
        
        Returns:
            BytesIO object containing the PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        # Container for elements
        elements = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold',
            borderPadding=5,
            backColor=colors.HexColor('#ecf0f1')
        )
        
        # Company Header
        elements.append(Paragraph(self.company_name, title_style))
        elements.append(Paragraph(self.company_address, subtitle_style))
        elements.append(Paragraph("<b>PAYSLIP</b>", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Payslip Info
        period_start = payroll_data.get('period_start', '')
        period_end = payroll_data.get('period_end', '')
        
        info_data = [
            ['Payslip Period:', f"{period_start} to {period_end}"],
            ['Generated On:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Payslip ID:', str(payroll_data.get('id', 'N/A'))]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7f8c8d')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2c3e50')),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Employee Information Section
        elements.append(Paragraph("Employee Information", section_style))
        
        emp_data = [
            ['Employee Name:', employee_data.get('name', 'N/A')],
            ['Employee ID:', str(employee_data.get('id', 'N/A'))],
            ['National ID:', employee_data.get('national_id', 'N/A')],
            ['Department:', employee_data.get('department', 'N/A')],
            ['Position:', employee_data.get('position', 'Employee')],
        ]
        
        emp_table = Table(emp_data, colWidths=[2*inch, 4*inch])
        emp_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7f8c8d')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2c3e50')),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(emp_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Earnings Section
        elements.append(Paragraph("Earnings", section_style))
        
        earnings_data = [
            ['Description', 'Amount (KSh)'],
            ['Basic Salary', f"{float(payroll_data.get('gross_salary', 0)):,.2f}"],
            ['Allowances', f"{float(payroll_data.get('allowances', 0)):,.2f}"],
            ['Bonuses', f"{float(payroll_data.get('bonuses', 0)):,.2f}"],
        ]
        
        earnings_table = Table(earnings_data, colWidths=[3*inch, 2.5*inch])
        earnings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
        ]))
        elements.append(earnings_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Deductions Section
        elements.append(Paragraph("Deductions", section_style))
        
        deductions_data = [
            ['Description', 'Amount (KSh)'],
            ['NSSF', f"{float(payroll_data.get('nssf', 0)):,.2f}"],
            ['NHIF', f"{float(payroll_data.get('nhif', 0)):,.2f}"],
            ['PAYE', f"{float(payroll_data.get('paye', 0)):,.2f}"],
            ['Housing Levy', f"{float(payroll_data.get('housing_levy', 0)):,.2f}"],
            ['Other Deductions', f"{float(payroll_data.get('other_deductions', 0)):,.2f}"],
            ['', ''],
            ['Total Deductions', f"{float(payroll_data.get('total_deductions', 0)):,.2f}"],
        ]
        
        deductions_table = Table(deductions_data, colWidths=[3*inch, 2.5*inch])
        deductions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -2), 1, colors.HexColor('#bdc3c7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BOTTOMPADDING', (0, 1), (-1, -2), 8),
            ('TOPPADDING', (0, 1), (-1, -2), 8),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#2c3e50')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
            ('TOPPADDING', (0, -1), (-1, -1), 10),
        ]))
        elements.append(deductions_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Net Salary Section
        net_data = [
            ['NET SALARY', f"KSh {float(payroll_data.get('net_salary', 0)):,.2f}"]
        ]
        
        net_table = Table(net_data, colWidths=[3*inch, 2.5*inch])
        net_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 16),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
            ('TOPPADDING', (0, 0), (-1, 0), 15),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#27ae60')),
        ]))
        elements.append(net_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#95a5a6'),
            alignment=TA_CENTER
        )
        
        elements.append(Paragraph("This is a computer-generated payslip and does not require a signature.", footer_style))
        elements.append(Paragraph(f"Generated by {self.company_name} HRMS", footer_style))
        
        # Build PDF
        doc.build(elements)
        
        buffer.seek(0)
        return buffer

# Initialize service
pdf_generator = PayslipPDFGenerator()
