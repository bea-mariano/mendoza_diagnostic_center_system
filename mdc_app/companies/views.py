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
from django.http import JsonResponse
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
from django.db.models import Q


from io import BytesIO
from datetime import datetime
from operator import attrgetter
from itertools import groupby

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfgen import canvas

from io import BytesIO
from datetime import datetime
from operator import attrgetter
from itertools import groupby

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfgen import canvas

from io import BytesIO
from datetime import datetime
from operator import attrgetter
from itertools import groupby

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfgen import canvas

def create_pdf(company, transactions):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 50
    available_width = width - 2 * margin

    styles = getSampleStyleSheet()
    normalStyle = styles['Normal']

    def draw_header():
        # Letterhead
        p.setFont("Helvetica-Bold", 16)
        p.drawString(margin, height - margin, "Mendoza Diagnostic Center")
        p.setFont("Helvetica", 9)
        p.drawString(margin, height - margin - 15,
                     "930 ME National Road, Tibag, Pulilan, Bulacan")
        p.drawString(margin, height - margin - 25,
                     '"Healthcare partner that is convenient, reliable, and affordable"')

        # Title
        p.setFont("Helvetica", 12)
        title = "STATEMENT OF ACCOUNT"
        tw = p.stringWidth(title, "Helvetica", 12)
        p.drawString((width - tw) / 2, height - margin - 45, title)

        # Company details
        hdr = [
            ["DATE", datetime.now().strftime('%B %d, %Y')],
            ["STATEMENT NO", f"{company.id}-{datetime.now().strftime('%Y%m')}"],
            ["ACCOUNT NAME", company.company_name]
        ]
        tbl = Table(hdr, colWidths=[available_width * 0.25, available_width * 0.75])
        tbl.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'Helvetica', 9),
            ('ALIGN',(0,0),(-1,-1),'LEFT'),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('BOTTOMPADDING',(0,0),(-1,-1),4),
            ('TOPPADDING',(0,0),(-1,-1),4),
        ]))
        y0 = height - margin - 65
        tbl.wrapOn(p, available_width, height)
        tbl.drawOn(p, margin, y0 - tbl._height)

        return y0 - tbl._height - 20  # top of body area

    # Prepare transaction rows
    header_row = ["DATE", "ID", "PATIENT NAME", "TRANSACTION TYPE", "AMOUNT"]
    detail_rows = []
    total_amount = 0.0
    for txn in transactions:
        amt = float(txn.formatted_discounted_total.replace(',', ''))
        total_amount += amt
        detail_rows.append([
            txn.transaction_date.strftime('%Y-%m-%d'),
            txn.id,
            str(txn.patient),
            Paragraph(str(txn.transaction_purpose), normalStyle),
            txn.formatted_discounted_total
        ])
    total_row = ["BALANCE DUE", "", "", "", f"{total_amount:,.2f}"]

    # Paginate every 25 rows
    rows_per_page = 25
    chunks = [
        detail_rows[i:i + rows_per_page]
        for i in range(0, len(detail_rows), rows_per_page)
    ]

    # Footer notes
    note_lines = [
        "*PLEASE MAKE YOUR PAYMENT WITHIN TEN (10) DAYS UPON RECEIPT OF THIS STATEMENT OF ACCOUNT",
        "*Please compare this statement of account with your records, and should there be any discrepancy",
        "please contact us at 0938-333-2349",
        "*Please make check payable to:",
        "ACCOUNT NAME: MENDOZA DIAGNOSTIC CENTER",
        "ACCOUNT NO: 413-7-41350801-7",
        "BANK NAME: METROBANK",
        "BANK BRANCH: PULILAN, BULACAN"
    ]
    line_height = 12
    notes_block_height = len(note_lines) * line_height + 10

    # 1) Draw all transaction pages
    for page_num, chunk in enumerate(chunks):
        if page_num > 0:
            p.showPage()
        y_body_start = draw_header()

        # Transactions heading
        p.setFont("Helvetica-Bold", 12)
        p.drawString(margin, y_body_start, "TRANSACTIONS")

        # Build table for this chunk
        table_data = [header_row] + chunk
        is_last_page = (page_num == len(chunks) - 1)
        # Only append total_row on same page if total transactions <= 12
        if is_last_page and len(detail_rows) <= 12:
            table_data.append(total_row)

        # Style
        table_style = [
            ('FONT',(0,0),(-1,0),'Helvetica-Bold',9),
            ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
            ('FONT',(0,1),(-1,-1),'Helvetica',9),
            ('ALIGN',(0,0),(-1,-1),'LEFT'),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('GRID',(0,0),(-1,-1),0.25,colors.black),
            ('ALIGN',(4,0),(4,-1),'RIGHT'),
        ]
        # Only style the balance row if it's on the same page
        if is_last_page and len(detail_rows) <= 12:
            table_style += [
                ('FONT',(0,-1),(-1,-1),'Helvetica-Bold',9),
                ('BACKGROUND',(0,-1),(-1,-1),colors.lightgrey),
                ('SPAN',(0,-1),(3,-1)),
                ('ALIGN',(0,-1),(0,-1),'RIGHT'),
            ]

        tbl = Table(table_data, colWidths=[
            available_width * 0.15,
            available_width * 0.10,
            available_width * 0.30,
            available_width * 0.30,
            available_width * 0.15,
        ])
        tbl.setStyle(TableStyle(table_style))
        tbl.wrapOn(p, available_width, height)
        bottom_y = y_body_start - 20 - tbl._height
        tbl.drawOn(p, margin, bottom_y)

    # 2) If more than 12 transactions, render summary & footers on a separate page
    if len(detail_rows) > 12:
        p.showPage()
        y_body_start = draw_header()

        # Commissions summary
        sorted_txns = sorted(transactions, key=attrgetter('payment_type'))
        summary = [["PAYMENT TYPE","TRANSACTION COUNT","PRICE PER EMPLOYEE","TOTAL"]]
        total_commission = 0.0
        for ptype, grp in groupby(sorted_txns, key=attrgetter('payment_type')):
            lst = list(grp)
            cnt = len(lst)
            com = 50.0
            total_commission += cnt * com
            summary.append([ptype, cnt, f"{com:,.2f}", f"{cnt*com:,.2f}"])
        summary.append(["ACCOUNT CURRENT REBATES","","",f"{total_commission:,.2f}"])

        p.setFont("Helvetica-Bold", 12)
        p.drawString(margin, y_body_start, "COMMISSIONS")
        tbl2 = Table(summary, colWidths=[
            available_width * 0.30,
            available_width * 0.25,
            available_width * 0.25,
            available_width * 0.20,
        ])
        tbl2.setStyle(TableStyle([
            ('FONT',(0,0),(-1,0),'Helvetica-Bold',9),
            ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
            ('GRID',(0,0),(-1,-1),0.25,colors.black),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONT',(0,-1),(-1,-1),'Helvetica-Bold',9),
            ('BACKGROUND',(0,-1),(-1,-1),colors.lightgrey),
            ('SPAN',(0,-1),(2,-1)),
            ('ALIGN',(0,-1),(0,-1),'RIGHT'),
        ]))
        tbl2.wrapOn(p, available_width, height)
        y_after_comm = y_body_start - 20 - tbl2._height
        tbl2.drawOn(p, margin, y_after_comm)

        # Balance summary
        p.setFont("Helvetica-Bold", 12)
        p.drawString(margin, y_after_comm - 40, "BALANCE SUMMARY")
        final_data = [
            ["BALANCE DUE", f"{total_amount:,.2f}"],
            ["CURRENT REBATES", f"{total_commission:,.2f}"],
            ["TOTAL BALANCE DUE", f"{total_amount - total_commission:,.2f}"],
        ]
        tbl3 = Table(final_data, colWidths=[available_width * 0.35, available_width * 0.15])
        tbl3.setStyle(TableStyle([
            ('FONT',(0,0),(-1,-1),'Helvetica-Bold',9),
            ('BACKGROUND',(0,0),(-1,-1),colors.whitesmoke),
            ('GRID',(0,0),(-1,-1),0.25,colors.black),
            ('ALIGN',(1,0),(1,-1),'RIGHT'),
        ]))
        tbl3.wrapOn(p, available_width, height)
        y_final = y_after_comm - 60 - tbl3._height
        tbl3.drawOn(p, margin, y_final)

        # Footers (notes)
        # Always have enough space—header + summary leaves room, but you could check again if needed
        notes_y = y_final - 30
        p.setFont("Helvetica-Bold", 9)
        p.drawString(margin, notes_y, note_lines[0])
        p.setFont("Helvetica", 9)
        for idx, line in enumerate(note_lines[1:], start=1):
            p.drawString(margin, notes_y - idx * line_height, line)

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
    ordering = ['company_name']

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            if q.isdigit():
                # search by numeric ID OR by name
                qs = qs.filter(
                    Q(id=int(q)) |
                    Q(company_name__icontains=q)
                )
            else:
                # search only by name
                qs = qs.filter(
                    Q(company_name__icontains=q)
                )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # so your template can pre‑fill the search box
        context['q'] = self.request.GET.get('q', '')
        return context

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

