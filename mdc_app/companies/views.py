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
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header for Mendoza Diagnostic Center
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "Mendoza Diagnostic Center")

    p.setFont("Helvetica", 10)
    p.drawString(50, 735, "930 ME National Road, Tibag, Pulilan, Bulacan")
    p.drawString(50, 725, '"Healthcare partner that is convenient, reliable, and affordable"')

    # STATEMENT OF ACCOUNT Title
    p.setFont("Helvetica", 12)
    page_width, _ = letter
    text = "STATEMENT OF ACCOUNT"
    text_width = p.stringWidth(text, "Helvetica", 12)
    x_center = (page_width - text_width) / 2
    p.drawString(x_center, 690, text)

    # Company details header table
    header_data = [
        ["DATE", datetime.now().strftime('%B %d, %Y')],
        ["STATEMENT NO", f"{company.id}-{datetime.now().strftime('%Y%m')}"] ,
        ["ACCOUNT NAME", company.company_name]
    ]

    available_width = width - 100
    header_table = Table(header_data, colWidths=[available_width * 0.25, available_width * 0.75])
    header_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))

    header_table_y = 660
    header_table.wrapOn(p, available_width, height)
    header_table.drawOn(p, 50, header_table_y - header_table._height)

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

    transactions_table = Table(transaction_data, colWidths=[
        available_width * 0.15, available_width * 0.10, available_width * 0.30,
        available_width * 0.30, available_width * 0.15
    ])

    last_row_index = len(transaction_data) - 1

    transactions_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('FONT', (0, last_row_index), (-1, last_row_index), 'Helvetica-Bold', 10),
        ('BACKGROUND', (0, last_row_index), (-1, last_row_index), colors.lightgrey),
        ('SPAN', (0, last_row_index), (3, last_row_index)),
        ('ALIGN', (0, last_row_index), (0, last_row_index), 'RIGHT'),
        ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
    ]))

    transactions_table_y = header_table_y - header_table._height - 20

    p.setFont("Helvetica", 10)
    p.drawString(50, transactions_table_y, "TRANSACTIONS")

    transactions_table_y = header_table_y - header_table._height - 35
    transactions_table.wrapOn(p, available_width, height)
    transactions_table.drawOn(p, 50, transactions_table_y - transactions_table._height)

    # Payment Type Summary Table
    # Sort transactions by payment_type to prepare for groupby
    sorted_transactions = sorted(transactions, key=attrgetter('payment_type'))

    # Initialize summary data
    summary_data = [["PAYMENT TYPE", "TRANSACTION COUNT", "PRICE PER EMPLOYEE", "TOTAL"]]

    # Group and summarize by payment_type
    for payment_type, group in groupby(sorted_transactions, key=attrgetter('payment_type')):
        group_list = list(group)
        count_txn = len(group_list)
        commission = float(50)
        # total = sum(float(txn.formatted_discounted_total.replace(',', '')) for txn in group_list)
        total = count_txn * commission

        summary_data.append([
            payment_type,
            count_txn,
            commission,
            f"{total:,.2f}"
        ])

    summary_table = Table(summary_data, colWidths=[
        available_width * 0.30, available_width * 0.25, available_width * 0.25, available_width * 0.20
    ])

    summary_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
    ]))

    summary_table_y = transactions_table_y - transactions_table._height - 30

    p.setFont("Helvetica", 10)
    p.drawString(50, summary_table_y, "COMMISSIONS")

    summary_table_y = transactions_table_y - transactions_table._height - 40
    summary_table.wrapOn(p, available_width, height)
    summary_table.drawOn(p, 50, summary_table_y - summary_table._height)

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