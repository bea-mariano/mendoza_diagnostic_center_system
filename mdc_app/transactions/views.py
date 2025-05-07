from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Transaction, TransactionTest
from .forms import TransactionForm
from companies.models import Company
from django.http import JsonResponse
from django.db.models import Q
from setpackages.models import Setpackage
from patients.models import Patient

from io import BytesIO
from django.http       import HttpResponse
from django.shortcuts  import get_object_or_404
from reportlab.lib     import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen  import canvas
from reportlab.platypus import Table, TableStyle
from django.contrib.staticfiles import finders

from .models import Transaction



@method_decorator(login_required, name='dispatch')
class TransactionListView(ListView):
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    ordering = ['-transaction_date', '-transaction_time']

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            if q.isdigit():
                # search by Txn ID, or by Patient ID or name
                qs = qs.filter(
                    Q(id=int(q)) |
                    Q(patient__id=int(q)) |
                    Q(patient__first_name__icontains=q) |
                    Q(patient__last_name__icontains=q)
                )
            else:
                # search only by patient name
                qs = qs.filter(
                    Q(patient__first_name__icontains=q) |
                    Q(patient__last_name__icontains=q)
                )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx

@method_decorator(login_required, name='dispatch')
class TransactionActiveListView(ListView):
    model = Transaction
    template_name = 'transactions/transaction_active_list.html'
    context_object_name = 'transactions'
    ordering = ['-transaction_date', '-transaction_time']

    def get_queryset(self):
        return Transaction.objects.ongoing()

@method_decorator(login_required, name='dispatch')
class TransactionDetailView(DetailView):
    model               = Transaction
    template_name       = 'transactions/transaction_detail.html'
    context_object_name = 'transaction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Build a simple list of applied discount names
        discounts = []
        txn = self.object
        if txn.is_philhealth:
            discounts.append('Philhealth')
        if txn.is_philhealth_free:
            discounts.append('Philhealth Free')
        if txn.is_senior_citizen:
            discounts.append('Senior Citizen')
        if txn.is_pwd:
            discounts.append('PWD')

        context['discounts'] = discounts  # e.g. ['Philhealth', 'PWD'] or []

        return context


class TransactionCreateView(CreateView):
    model         = Transaction
    form_class    = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url   = reverse_lazy('transaction_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['patients'] = Patient.objects.all()
        return ctx

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # DEBUG: show raw POST discounts
        selected = self.request.POST.getlist('discounts')
        print("🛠️ DEBUG - Submitted discounts:", selected)

        self.object.is_philhealth      = 'Philhealth' in selected or 'Philhealth 700' in selected
        self.object.is_philhealth_free = 'Philhealth Free' in selected
        self.object.is_senior_citizen  = 'Senior Citizen' in selected
        self.object.is_pwd             = 'PWD' in selected

        base = self.object.transaction_total
        rate = 0

        print(f"🧮 DEBUG - Base transaction total: {base}")
        print(f"🧾 DEBUG - is_philhealth: {self.object.is_philhealth}")
        print(f"🧾 DEBUG - is_philhealth_free: {self.object.is_philhealth_free}")
        print(f"🧾 DEBUG - is_senior_citizen: {self.object.is_senior_citizen}")
        print(f"🧾 DEBUG - is_pwd: {self.object.is_pwd}")

        if self.object.is_philhealth_free:
            rate = base
            print("📢 DEBUG - Philhealth Free applied → full discount")
        else:
            if 'Philhealth 700' in selected:
                rate += 700
                print("✅ DEBUG - Philhealth 700 applied")
            elif 'Philhealth' in selected:
                rate += 500
                print("✅ DEBUG - Philhealth 500 applied")

            if self.object.is_senior_citizen or self.object.is_pwd:
                senior_pwd_discount = round(base * 0.2)
                print(f"✅ DEBUG - SC/PWD discount: {senior_pwd_discount}")
                rate += senior_pwd_discount

        self.object.discount_rate = rate
        self.object.discounted_total = max(base - rate, 0)

        print(f"🎯 DEBUG - Final Discount Rate: {rate}")
        print(f"🎯 DEBUG - Final Discounted Total: {self.object.discounted_total}")

        self.object.save()
        form.save_m2m()

        for test in form.cleaned_data.get('tests', []):
            TransactionTest.objects.create(
                transaction=self.object,
                test=test,
                test_price=test.test_price
            )

        return redirect(self.success_url)



class TransactionUpdateView(UpdateView):
    model         = Transaction
    form_class    = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url   = reverse_lazy('transaction_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['patients'] = Patient.objects.all()
        return ctx

    def form_valid(self, form):
        self.object = form.save(commit=False)

        tp = self.request.POST.get('transaction_purpose') or form.cleaned_data.get('transaction_purpose')
        self.object.transaction_purpose = tp.strip() if tp else None

        pkg = None
        if self.object.company_id and self.object.transaction_purpose:
            pkg = Setpackage.objects.filter(
                company=self.object.company,
                package_transaction_purpose__iexact=self.object.transaction_purpose
            ).first()
        self.object.setpackage = pkg

        self.object.transaction_status = form.cleaned_data.get('transaction_status', 'Ongoing')
        if not self.object.payment_type:
            self.object.payment_type = 'Cash'

        # Unified discount logic
        selected = self.request.POST.getlist('discounts')
        print("🛠️ DEBUG - Submitted discounts:", selected)

        self.object.is_philhealth      = 'Philhealth' in selected or 'Philhealth 700' in selected
        self.object.is_philhealth_free = 'Philhealth Free' in selected
        self.object.is_senior_citizen  = 'Senior Citizen' in selected
        self.object.is_pwd             = 'PWD' in selected

        base = self.object.transaction_total
        rate = 0

        print(f"🧮 DEBUG - Base transaction total: {base}")
        print(f"🧾 DEBUG - is_philhealth: {self.object.is_philhealth}")
        print(f"🧾 DEBUG - is_philhealth_free: {self.object.is_philhealth_free}")
        print(f"🧾 DEBUG - is_senior_citizen: {self.object.is_senior_citizen}")
        print(f"🧾 DEBUG - is_pwd: {self.object.is_pwd}")

        if self.object.is_philhealth_free:
            rate = base
            print("📢 DEBUG - Philhealth Free applied → full discount")
        else:
            if 'Philhealth 700' in selected:
                rate += 700
                print("✅ DEBUG - Philhealth 700 applied")
            elif 'Philhealth' in selected:
                rate += 500
                print("✅ DEBUG - Philhealth 500 applied")

            if self.object.is_senior_citizen or self.object.is_pwd:
                senior_pwd_discount = round(base * 0.2)
                print(f"✅ DEBUG - SC/PWD discount: {senior_pwd_discount}")
                rate += senior_pwd_discount

        self.object.discount_rate = rate
        self.object.discounted_total = max(base - rate, 0)

        print(f"🎯 DEBUG - Final Discount Rate: {rate}")
        print(f"🎯 DEBUG - Final Discounted Total: {self.object.discounted_total}")

        self.object.save()
        form.save_m2m()

        self.object.transaction_tests.all().delete()
        for test in form.cleaned_data.get('tests', []):
            TransactionTest.objects.create(
                transaction=self.object,
                test=test,
                test_price=test.test_price
            )

        return redirect(self.success_url)




@method_decorator(login_required, name='dispatch')
class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = 'transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')


@login_required
def complete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    transaction.transaction_status = 'Completed'
    transaction.save()
    return redirect('transaction_detail', pk=pk)

@login_required
def revert_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    transaction.transaction_status = 'Ongoing'
    transaction.save()
    return redirect('transaction_detail', pk=pk)

def get_company_peme_rate(request, company_id):
    try:
        company = Company.objects.get(pk=company_id)
        return JsonResponse({'peme_rate': company.company_peme_rate})
    except Company.DoesNotExist:
        return JsonResponse({'peme_rate': 0})
    
from io import BytesIO
from django.http       import HttpResponse
from django.shortcuts  import get_object_or_404
from reportlab.lib     import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen  import canvas
from reportlab.platypus import Table, TableStyle

from .models import Transaction

from io import BytesIO
from django.http       import HttpResponse
from django.shortcuts  import get_object_or_404
from reportlab.lib     import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen  import canvas
from reportlab.platypus import Table, TableStyle

from django.templatetags.static import static
from reportlab.lib.utils import ImageReader

from .models import Transaction

def transaction_lab_pdf(request, pk):
    txn = get_object_or_404(Transaction, pk=pk)

    buf   = BytesIO()
    p     = canvas.Canvas(buf, pagesize=letter)
    width, height   = letter
    margin  = 40
    avail   = width - 2*margin
    gap     = 6

    # Add logo after canvas is created
    # Use Django staticfiles finders to get the full file path
    logo_path = finders.find("images/mdc_logo.jpg")  # adjust if your path differs

    logo_width = 50
    logo_height = 50
    if logo_path:
        p.drawImage(
            ImageReader(logo_path),
            x=margin,
            y=height - (margin+15),
            width=40,
            height=40,
            preserveAspectRatio=True,
            mask='auto'
        )


    # Header
    y = height - margin
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin + 50, y, "Mendoza Diagnostic Center")
    p.setFont("Helvetica", 10)
    p.drawString(margin + 50, y - 15, "Laboratory Working Paper")
    p.line(margin, y - 20, width - margin, y - 20)

    dob     = txn.patient.date_of_birth
    tx_date = txn.transaction_date
    age     = (
        tx_date.year - dob.year
        - ((tx_date.month, tx_date.day) < (dob.month, dob.day))
    )
    name    = f"{txn.patient.last_name}, {txn.patient.first_name}"
    gender  = txn.patient.get_gender_display()
    contact = txn.contact_no
    addr    = txn.address

    # Style for each small table
    style = TableStyle([
        ("FONT",       (0,0), (-1,-1), "Helvetica", 9),
        ("GRID",       (0,0), (-1,-1), 0.25, colors.black),
        ("BACKGROUND", (0,0), (0,0),   colors.lightgrey),
    ])

    basic_style = TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
        # no GRID, no BACKGROUND
    ])

    # Start drawing groups below header
    y -= 30
    row_spacing = -3

    # --- Group 1: Transaction ID (60%) | Date (20%) ---
    tx_w   = avail * 0.48
    date_w = avail * 0.52
    # Transaction ID table
    tbl_tx = Table([[ "Transaction ID", f":    {str(txn.id)}" ]],
                   colWidths=[tx_w * 0.25, tx_w * 0.75])
    tbl_tx.setStyle(basic_style)
    tbl_tx.wrapOn(p, margin, y)
    tbl_tx.drawOn(p, margin, y - tbl_tx._height)
    # Date table
    tbl_dt = Table([[ "Date", f""":    {tx_date.strftime("%Y-%m-%d")}""" ]],
                   colWidths=[date_w * 0.3, date_w * 0.7])
    tbl_dt.setStyle(basic_style)
    x_dt = margin + tx_w + gap
    tbl_dt.wrapOn(p, x_dt, y)
    tbl_dt.drawOn(p, x_dt, y - tbl_dt._height)
    y -= tbl_tx._height + row_spacing

    # --- Group 2: Patient ID (60%) | Gender (20%) ---
    tbl_pid = Table([[ "Patient ID", f":    {str(txn.patient.id)}" ]],
                    colWidths=[tx_w * 0.25, tx_w * 0.75])
    tbl_pid.setStyle(basic_style)
    tbl_pid.wrapOn(p, margin, y)
    tbl_pid.drawOn(p, margin, y - tbl_pid._height)

    tbl_gn = Table([[ "Gender", f":    {gender}" ]],
                   colWidths=[date_w * 0.3, date_w * 0.7])
    tbl_gn.setStyle(basic_style)
    tbl_gn.wrapOn(p, margin+tx_w+gap, y)
    tbl_gn.drawOn(p, margin+tx_w+gap, y - tbl_gn._height)
    y -= tbl_pid._height + row_spacing

    # --- Group 3: Name (60%) | Age (20%) ---
    tbl_nm = Table([[ "Name", f":    {name}" ]],
                   colWidths=[tx_w * 0.25, tx_w * 0.75])
    tbl_nm.setStyle(basic_style)
    tbl_nm.wrapOn(p, margin, y)
    tbl_nm.drawOn(p, margin, y - tbl_nm._height)

    tbl_ag = Table([[ "Age", f":    {str(age)}" ]],
                   colWidths=[date_w * 0.3, date_w * 0.7])
    tbl_ag.setStyle(basic_style)
    tbl_ag.wrapOn(p, margin+tx_w+gap, y)
    tbl_ag.drawOn(p, margin+tx_w+gap, y - tbl_ag._height)
    y -= tbl_nm._height + row_spacing

    # --- Group 4: Birthdate (60%) | Contact No. (20%) ---
    tbl_bd = Table([[ "Birthdate", f""":    {dob.strftime("%Y-%m-%d")}""" ]],
                   colWidths=[tx_w * 0.25, tx_w * 0.75])
    tbl_bd.setStyle(basic_style)
    tbl_bd.wrapOn(p, margin, y)
    tbl_bd.drawOn(p, margin, y - tbl_bd._height)

    tbl_cn = Table([[ "Contact No.", f":    {contact}" ]],
                   colWidths=[date_w * 0.3, date_w * 0.7])
    tbl_cn.setStyle(basic_style)
    tbl_cn.wrapOn(p, margin+tx_w+gap, y)
    tbl_cn.drawOn(p, margin+tx_w+gap, y - tbl_cn._height)
    y -= tbl_bd._height + row_spacing

    # --- Group 6: Package Name (60%) | Company (20%) ---
    tbl_pkg = Table([[ "Package Name", f":    {txn.transaction_purpose}" ]],
                    colWidths=[tx_w * 0.25, tx_w * 0.75])
    tbl_pkg.setStyle(basic_style)
    tbl_pkg.wrapOn(p, margin, y)
    tbl_pkg.drawOn(p, margin, y - tbl_pkg._height)

    tbl_cmp = Table([[ "Company", f":    {txn.company.company_name}" ]],
                    colWidths=[date_w * 0.3, date_w * 0.7])
    tbl_cmp.setStyle(basic_style)
    tbl_cmp.wrapOn(p, margin + tx_w + gap, y)
    tbl_cmp.drawOn(p, margin + tx_w + gap, y - tbl_cmp._height)
    y -= tbl_cmp._height + row_spacing


    # --- Group 5: Address full width (100%) ---
    tbl_ad = Table([[ "Address", f":    {addr}" ]],
                   colWidths=[avail * 0.15, avail * 0.85])
    tbl_ad.setStyle(basic_style)
    tbl_ad.wrapOn(p, margin, y)
    tbl_ad.drawOn(p, margin, y - tbl_ad._height)
    y -= tbl_ad._height + row_spacing + 10

    # --- Tests (names only, no borders, no header) ---
    tests_data = [
        [tt.test.test_name]
        for tt in txn.transaction_tests.all()
    ]

    tbl_tests = Table(tests_data, colWidths=[avail])
    tbl_tests.setStyle(TableStyle([
        ("FONT",       (0, 0), (-1, -1), "Helvetica", 7),
        ("TEXTCOLOR",  (0, 0), (-1, -1), colors.red),
    ]))
    tbl_tests.wrapOn(p, margin, y)
    tbl_tests.drawOn(p, margin, y - tbl_tests._height)


    # Finish PDF
    p.showPage()
    p.save()

    pdf = buf.getvalue()
    buf.close()
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="lab_worksheet_{txn.id}.pdf"'
    return resp


# ------- REPORTS VIEWS ----------
from django.utils import timezone
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

import pytz
from datetime import datetime

from .models import Transaction

def get_manila_date():
    return timezone.now().astimezone(pytz.timezone('Asia/Manila')).date()

@method_decorator(login_required, name='dispatch')
class TransactionFilteredReportView(ListView):
    model = Transaction
    template_name = 'transactions/report_home.html'
    context_object_name = 'transactions'
    ordering = ['-transaction_date', '-transaction_time']

    def get_queryset(self):
        qs = super().get_queryset()
        q_date_start = self.request.GET.get('start_date')
        q_date_end   = self.request.GET.get('end_date')
        payment_type = self.request.GET.get('payment_type')

        if q_date_start and q_date_end:
            try:
                date_start = datetime.strptime(q_date_start, '%Y-%m-%d').date()
                date_end = datetime.strptime(q_date_end, '%Y-%m-%d').date()
                qs = qs.filter(transaction_date__range=(date_start, date_end))
            except ValueError:
                pass
        elif q_date_start:
            try:
                date_start = datetime.strptime(q_date_start, '%Y-%m-%d').date()
                qs = qs.filter(transaction_date=date_start)
            except ValueError:
                pass

        if payment_type in ['Cash', 'Charged']:
            qs = qs.filter(payment_type__iexact=payment_type)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['start_date'] = self.request.GET.get('start_date', '')
        ctx['end_date'] = self.request.GET.get('end_date', '')
        ctx['payment_type'] = self.request.GET.get('payment_type', '')
        return ctx
