# companies/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Company
from .forms import CompanyForm
from transactions.models import Transaction
from transactions.forms import TransactionForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from collections import defaultdict
from django.db.models import Sum, Count

from itertools import groupby
from operator import attrgetter


def create_pdf(company, transactions):
    buffer = BytesIO()
    # Change from letter to legal size
    legal = (612, 1008)  # Legal size in points (8.5 x 14 inches)
    p = canvas.Canvas(buffer, pagesize=legal)
    width, height = legal
    page_num = 1
    
    # Function to create header on each page
    def add_header(canvas_obj, page_number):
        # Header for Mendoza Diagnostic Center
        canvas_obj.setFont("Helvetica-Bold", 16)
        canvas_obj.drawString(50, height - 50, "Mendoza Diagnostic Center")
        
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.drawString(50, height - 65, "930 ME National Road, Tibag, Pulilan, Bulacan")
        canvas_obj.drawString(50, height - 75, '"Healthcare partner that is convenient, reliable, and affordable"')
        
        # Page number
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.drawString(width - 70, height - 50, f"Page {page_number}")
        
        # STATEMENT OF ACCOUNT Title
        canvas_obj.setFont("Helvetica", 12)
        text = "STATEMENT OF ACCOUNT"
        text_width = canvas_obj.stringWidth(text, "Helvetica", 12)
        x_center = (width - text_width) / 2
        canvas_obj.drawString(x_center, height - 100, text)
        
        return height - 100  # Return the y position after the header

    # Add first page header
    current_y = add_header(p, page_num)
    
    # Company details header table
    header_data = [
        ["DATE", datetime.now().strftime('%B %d, %Y')],
        ["STATEMENT NO", f"{company.id}-{datetime.now().strftime('%Y%m')}"],
        ["ACCOUNT NAME", company.company_name]
    ]
    
    available_width = width - 100
    header_table = Table(header_data, colWidths=[available_width * 0.25, available_width * 0.75])
    header_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    header_table_y = current_y - 30
    header_table.wrapOn(p, available_width, height)
    header_table.drawOn(p, 50, header_table_y - header_table._height)
    
    current_y = header_table_y - header_table._height - 20
    
    styles = getSampleStyleSheet()
    normalStyle = styles['Normal']
    
    # Transactions table
    transaction_data = [["DATE", "ID", "PATIENT NAME", "TRANSACTION TYPE", "AMOUNT"]]
    total_amount = 0
    for txn in transactions:
        amount_value = float(txn.formatted_discounted_total.replace(',', ''))
        total_amount += amount_value
        transaction_data.append([
            txn.transaction_date.strftime('%Y-%m-%d'),
            txn.id,
            str(txn.patient),
            Paragraph(str(txn.transaction_purpose), normalStyle),
            txn.formatted_discounted_total
        ])
    
    total_formatted = "{:,.2f}".format(total_amount)
    transaction_data.append(["BALANCE DUE", "", "", "", total_formatted])
    
    last_row_index = len(transaction_data) - 1
    
    # Calculate transaction table height to check if it fits on the page
    transactions_table_style = TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('FONT', (0, last_row_index), (-1, last_row_index), 'Helvetica-Bold', 9),
        ('BACKGROUND', (0, last_row_index), (-1, last_row_index), colors.lightgrey),
        ('SPAN', (0, last_row_index), (3, last_row_index)),
        ('ALIGN', (0, last_row_index), (0, last_row_index), 'RIGHT'),
        ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
    ])
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, current_y, "TRANSACTIONS")
    current_y -= 15
    
    # Split transactions into chunks if needed for pagination
    def chunks(data, header_row, rows_per_page):
        result = []
        chunk = [header_row]
        
        for i, row in enumerate(data[1:], 1):
            # Skip header row for subsequent chunks
            if i == last_row_index:  # Keep total row for the last chunk only
                continue
            
            chunk.append(row)
            
            if len(chunk) == rows_per_page and i < last_row_index - 1:
                result.append(chunk)
                chunk = [header_row]  # Start new chunk with header
        
        # Add total row to the last chunk if not already included
        if data[last_row_index] not in chunk:
            chunk.append(data[last_row_index])
        
        result.append(chunk)
        return result
    
    # Estimate rows per page - increase for legal size
    # Legal size is taller than letter, so we can fit more rows
    rows_per_page = 30  # Adjusted for legal size
    
    transaction_chunks = chunks(transaction_data, transaction_data[0], rows_per_page) 
    
    for i, chunk in enumerate(transaction_chunks):
        if i > 0:
            # Start a new page
            p.showPage()
            page_num += 1
            current_y = add_header(p, page_num)
            
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, current_y - 15, "TRANSACTIONS (continued)")
            current_y -= 30
        
        # Create table for current chunk
        transactions_table = Table(chunk, colWidths=[
            available_width * 0.15, available_width * 0.10, available_width * 0.30,
            available_width * 0.30, available_width * 0.15
        ])
        
        transactions_table.setStyle(transactions_table_style)
        
        transactions_table.wrapOn(p, available_width, height)
        transactions_table.drawOn(p, 50, current_y - transactions_table._height)
        
        current_y = current_y - transactions_table._height - 20
    
    # Check if there's enough space for Payment Type Summary Table
    # Adjusted for legal size - need more space
    if current_y < 200:
        p.showPage()
        page_num += 1
        current_y = add_header(p, page_num) - 30
    
    # Sort transactions by payment_type to prepare for groupby
    sorted_transactions = sorted(transactions, key=attrgetter('payment_type'))
    
    summary_data = [["PAYMENT TYPE", "TRANSACTION COUNT", "PRICE PER EMPLOYEE", "TOTAL"]]
    total_commission = 0
    
    for payment_type, group in groupby(sorted_transactions, key=attrgetter('payment_type')):
        group_list = list(group)
        count_txn = len(group_list)
        commission = float(50)
        total = count_txn * commission
        total_commission += total
        
        summary_data.append([
            payment_type,
            count_txn,
            f"{commission:,.2f}",
            f"{total:,.2f}"
        ])
    
    # Add total row
    summary_data.append([
        "ACCOUNT CURRENT REBATES", "", "",
        f"{total_commission:,.2f}"
    ])
    
    summary_table = Table(summary_data, colWidths=[
        available_width * 0.30, available_width * 0.25, available_width * 0.25, available_width * 0.20
    ])
    
    summary_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 9),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('SPAN', (0, -1), (2, -1)),
        ('ALIGN', (0, -1), (0, -1), 'RIGHT'),
    ]))
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, current_y, "COMMISSIONS")
    current_y -= 15
    
    summary_table.wrapOn(p, available_width, height)
    summary_table.drawOn(p, 50, current_y - summary_table._height)
    
    current_y = current_y - summary_table._height - 20
    
    # Check if there's enough space for Balance Summary and Notes
    # Adjusted for legal size
    if current_y < 250:
        p.showPage()
        page_num += 1
        current_y = add_header(p, page_num) - 30
    
    # Final Balance Due Summary Table
    final_summary_data = [
        ["BALANCE DUE", f"{total_amount:,.2f}"],
        ["CURRENT REBATES", f"{total_commission:,.2f}"],
        ["TOTAL BALANCE DUE", f"{total_amount - total_commission:,.2f}"]
    ]
    
    final_summary_table = Table(final_summary_data, colWidths=[available_width * 0.35, available_width * 0.15])
    final_summary_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 9),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, current_y, "BALANCE SUMMARY")
    current_y -= 15
    
    final_summary_table.wrapOn(p, available_width, height)
    final_summary_table.drawOn(p, 50, current_y - final_summary_table._height)
    
    current_y = current_y - final_summary_table._height - 20
    
    # Check if there's enough space for Notes section
    # Adjusted for legal size
    if current_y < 250:
        p.showPage()
        page_num += 1
        current_y = add_header(p, page_num) - 30
    
    # Notes section
    p.setFont("Helvetica-Bold", 9)
    p.drawString(50, current_y, "Prepared By:")
    p.drawString(50, current_y - 25, "Diosa M. Mendoza")
    p.setFont("Helvetica", 9)
    p.drawString(50, current_y - 35, "Accounting")
    
    p.setFont("Helvetica-Bold", 9)
    p.drawString(250, current_y, "Checked By:")
    p.drawString(250, current_y - 25, "Lovelie Joy M. Mendoza")
    p.setFont("Helvetica", 9)
    p.drawString(250, current_y - 35, "Manager")
    
    current_y -= 60
    
    p.setFont("Helvetica-Bold", 9)
    p.drawString(50, current_y, "*PLEASE MAKE YOUR PAYMENT WITHIN TEN (10) DAYS UPON RECEIPT OF THIS STATEMENT OF ACCOUNT")
    
    p.setFont("Helvetica", 9)
    p.drawString(50, current_y - 15, "*Please compare this statement of account with your records, and should there be any discrepancy")
    p.drawString(50, current_y - 30, "please contact us at 0938-333-2349")
    p.drawString(50, current_y - 45, "*Please make check payable to:")
    p.drawString(50, current_y - 60, "ACCOUNT NAME: MENDOZA DIAGNOSTIC CENTER")
    p.drawString(50, current_y - 75, "ACCOUNT NO: 413-7-41350801-7")
    p.drawString(50, current_y - 90, "BANK NAME: METROBANK")
    p.drawString(50, current_y - 105, "BANK BRANCH: PULILAN, BULACAN")
    
    # Finish up the PDF
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf



def generate_statement(request, company_id):
    company = get_object_or_404(Company, pk=company_id)

    month_str = request.GET.get('month')
    if not month_str:
        return HttpResponse("Month not specified", status=400)

    try:
        selected_date = datetime.strptime(month_str, "%Y-%m")
    except ValueError:
        return HttpResponse("Invalid month format", status=400)

    transactions = Transaction.objects.filter(
        company=company,
        transaction_status='Completed',
        transaction_date__year=selected_date.year,
        transaction_date__month=selected_date.month
    )

    # Format discounted_total in accounting style
    for transaction in transactions:
        transaction.formatted_discounted_total = "{:,.2f}".format(transaction.discounted_total)

    # Implement create_pdf to use formatted_discounted_total
    pdf_content = create_pdf(company, transactions)

    response = HttpResponse(pdf_content, content_type='application/pdf')
    filename = f"statement_{company.id}_{month_str}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@method_decorator(login_required, name='dispatch')
class CompanyListView(ListView):
    model = Company
    template_name = 'companies/company_list.html'
    context_object_name = 'companies'

@method_decorator(login_required, name='dispatch')
class CompanyDetailView(DetailView):
    model = Company
    template_name = 'companies/company_detail.html'
    context_object_name = 'company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.object
        context['transactions'] = Transaction.objects.filter(company=company)
        return context

@method_decorator(login_required, name='dispatch')
class CompanyCreateView(CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'companies/company_form.html'
    success_url = reverse_lazy('company_new')

    def form_valid(self, form):
        data = form.cleaned_data
        existing_company = Company.objects.filter(
            company_name__iexact=data['company_name']
        ).first()

        if existing_company:
            # Pass this info to template context
            return self.render_to_response(self.get_context_data(
                form=form,
                existing_company=existing_company,
                show_modal=True,
                modal_message=f"Company already exists with ID {existing_company.id}"
            ))
        else:
            self.object = form.save()
            return self.render_to_response(self.get_context_data(
                form=self.get_form_class()(instance=self.object),
                new_company=self.object,
                show_modal=True,
                modal_message=f"New company created with ID {self.object.id}"
            ))

@method_decorator(login_required, name='dispatch')
class CompanyUpdateView(UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'companies/company_form.html'
    success_url = reverse_lazy('company_list')

@method_decorator(login_required, name='dispatch')
class CompanyDeleteView(DeleteView):
    model = Company
    template_name = 'companies/company_confirm_delete.html'
    success_url = reverse_lazy('company_list')