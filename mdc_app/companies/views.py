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

def create_pdf(company, transactions):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header for Mendoza Diagnostic Center
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "Mendoza Diagnostic Center")

    p.setFont("Helvetica", 10)
    p.drawString(50, 735, "930 ME National Road, Tibag, Pulilan, Bulacan")
    p.drawString(50, 725, "\"Healthcare partner that is convenient, reliable, and affordable\"")

    # Centered STATEMENT OF ACCOUNT Title
    p.setFont("Helvetica", 12)
    page_width, _ = letter
    text = "STATEMENT OF ACCOUNT"
    text_width = p.stringWidth(text, "Helvetica", 12)
    x_center = (page_width - text_width) / 2
    p.drawString(x_center, 690, text)

    # Build the header table for company details (two columns: label and value)
    header_data = [
        ["DATE", datetime.now().strftime('%B %d, %Y')],
        ["STATEMENT NO", f"{company.id}-{datetime.now().strftime('%Y%m')}"],
        ["ACCOUNT NAME", company.company_name]
    ]

    available_width = width - 100  # 50 pt margin on each side
    header_table = Table(header_data, colWidths=[available_width * 0.25, available_width * 0.75])
    header_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        # Uncomment to add borders:
        # ('GRID', (0,0), (-1,-1), 0.25, colors.black)
    ]))

    # Position the header table below the title
    table_x = 50
    header_table_y = 670  # top position for the company header table
    header_table.wrapOn(p, available_width, height)
    header_table.drawOn(p, table_x, header_table_y - header_table._height)

    # Prepare a style for paragraphs for text wrapping
    styles = getSampleStyleSheet()
    normalStyle = styles['Normal']

    # Build the transactions table data.
    # Header row for the transactions table.
    transaction_data = [["DATE (YYYY-MM-DD)", "ID", "PATIENT NAME", "TRANSACTION TYPE", "AMOUNT (Php)"]]

    # Add each transaction as a row.
    for txn in transactions:
        transaction_data.append([
            txn.transaction_date.strftime('%Y-%m-%d'),
            txn.id,
            # Convert the Patient object into a string; alternatively, use txn.patient.name if available.
            str(txn.patient),
            # Wrap the transaction type in Paragraph for proper text wrapping.
            Paragraph(str(txn.transaction_purpose), normalStyle),
            txn.discounted_total
        ])

    # Create the transactions table with specific column widths.
    transactions_table = Table(transaction_data, colWidths=[
            available_width * 0.15,  # DATE
            available_width * 0.10,  # ID
            available_width * 0.30,  # PATIENT NAME
            available_width * 0.25,  # TRANSACTION TYPE
            available_width * 0.15   # AMOUNT
        ])
    transactions_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),  # header row bold
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black)
    ]))

    # Position the transactions table below the company header table with a gap
    gap = 30
    transactions_table_y = header_table_y - header_table._height - gap
    transactions_table.wrapOn(p, available_width, height)
    transactions_table.drawOn(p, 50, transactions_table_y - transactions_table._height)

    # Finish up the PDF
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def generate_statement(request, company_id):
    # Retrieve the company instance
    company = get_object_or_404(Company, pk=company_id)

    # Get the selected month from the query string (expects a format like "2025-04")
    month_str = request.GET.get('month')
    if not month_str:
        return HttpResponse("Month not specified", status=400)
    
    try:
        # Parse the month; day is irrelevant here so we use the first day of the month
        selected_date = datetime.strptime(month_str, "%Y-%m")
    except ValueError:
        return HttpResponse("Invalid month format", status=400)

    # Filter transactions for the given company, status "Completed",
    # and matching the selected month and year
    transactions = Transaction.objects.filter(
        company=company,
        transaction_status='Completed',
        transaction_date__year=selected_date.year,
        transaction_date__month=selected_date.month
    )

    # Generate the PDF using your preferred PDF library.
    # Example: pdf_content = create_pdf(company, transactions)
    pdf_content = create_pdf(company, transactions)  # Implement this helper accordingly

    # Send the PDF file as a downloadable response
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