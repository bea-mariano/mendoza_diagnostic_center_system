from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Q
from django.db import IntegrityError
import logging

from .models import Setpackage, SetpackageTest
from .forms import SetpackageForm
from tests.models import Test

logger = logging.getLogger('mdc_app')


@method_decorator(login_required, name='dispatch')
class SetpackageListView(ListView):
    model = Setpackage
    template_name = 'setpackages/setpackage_list.html'
    context_object_name = 'setpackages'

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            if q.isdigit():
                qs = qs.filter(
                    Q(id=int(q)) |
                    Q(package_name__icontains=q)
                )
            else:
                qs = qs.filter(
                    Q(package_name__icontains=q)
                )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context


@method_decorator(login_required, name='dispatch')
class SetpackageDetailView(DetailView):
    model = Setpackage
    template_name = 'setpackages/setpackage_detail.html'
    context_object_name = 'setpackage'


@method_decorator(login_required, name='dispatch')
class SetpackageCreateView(CreateView):
    model = Setpackage
    form_class = SetpackageForm
    template_name = 'setpackages/setpackage_form.html'
    success_url = reverse_lazy('setpackage_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tests'] = Test.objects.all()
        return context

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        non_field = form.non_field_errors()
        if non_field:
            context.update({
                'show_modal': True,
                'modal_message': non_field[0],
                'existing_setpackage': Setpackage.objects.filter(
                    company=form.cleaned_data.get('company'),
                    package_name__iexact=form.cleaned_data.get('package_name'),
                    package_transaction_purpose__iexact=form.cleaned_data.get('package_transaction_purpose')
                ).first()
            })
        return self.render_to_response(context)

    def form_valid(self, form):
        data = form.cleaned_data
        existing = Setpackage.objects.filter(
            company=data['company'],
            package_name__iexact=data['package_name'],
            package_transaction_purpose__iexact=data['package_transaction_purpose']
        ).first()

        username = (
            self.request.user.username
            if self.request.user.is_authenticated
            else 'anonymous'
        )

        if existing:
            logger.info(
                f"Package CREATE attempted by user={username!r}: already exists (ID={existing.id})"
            )
            form.add_error(
                None,
                f"A package '{existing.package_name}' for purpose '{existing.package_transaction_purpose}' "
                f"already exists under {existing.company.company_name} (ID {existing.id})."
            )
            return self.form_invalid(form)

        try:
            self.object = form.save()
        except IntegrityError:
            logger.info(
                f"INTEGRITY ERROR: Package CREATE attempted by user={username!r}"
            )
            form.add_error(
                None,
                f"A package '{data['package_name']}' for purpose '{data['package_transaction_purpose']}' "
                f"already exists under {data['company'].company_name}."
            )
            return self.form_invalid(form)

        for test_id in self.request.POST.getlist('tests'):
            exclusion_val = self.request.POST.get(f'exclusion_{test_id}', '')
            try:
                exclusion_amount = float(exclusion_val)
            except (ValueError, TypeError):
                continue
            SetpackageTest.objects.create(
                package=self.object,
                test_id=test_id,
                exclusion_amount=exclusion_amount
            )

        return redirect(self.success_url)


@method_decorator(login_required, name='dispatch')
class SetpackageUpdateView(UpdateView):
    model = Setpackage
    form_class = SetpackageForm
    template_name = 'setpackages/setpackage_form.html'
    success_url = reverse_lazy('setpackage_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_tests = Test.objects.all()
        existing_tests = {pt.test_id: pt.exclusion_amount for pt in self.object.tests.all()}
        for test in all_tests:
            test.is_checked = test.id in existing_tests
            test.exclusion_amount = existing_tests.get(test.id, "")
        context['tests'] = all_tests
        return context

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        non_field = form.non_field_errors()
        if non_field:
            context.update({
                'show_modal': True,
                'modal_message': non_field[0],
                'existing_setpackage': Setpackage.objects.filter(
                    company=form.cleaned_data.get('company'),
                    package_name__iexact=form.cleaned_data.get('package_name'),
                    package_transaction_purpose__iexact=form.cleaned_data.get('package_transaction_purpose')
                ).exclude(pk=self.get_object().pk).first()
            })
        return self.render_to_response(context)

    def form_valid(self, form):
        data = form.cleaned_data
        obj_pk = self.get_object().pk
        existing = Setpackage.objects.filter(
            company=data['company'],
            package_name__iexact=data['package_name'],
            package_transaction_purpose__iexact=data['package_transaction_purpose']
        ).exclude(pk=obj_pk).first()

        username = (
            self.request.user.username if self.request.user.is_authenticated else 'anonymous'
        )
        if existing:
            logger.info(
                f"Package UPDATE attempted by user={username!r}: conflict with ID={existing.id}"
            )
            form.add_error(
                None,
                f"Another package '{existing.package_name}' for purpose '{existing.package_transaction_purpose}' "
                f"already exists under {existing.company.company_name} (ID {existing.id})."
            )
            return self.form_invalid(form)

        self.object = form.save()
        self.object.tests.all().delete()
        for test_id in self.request.POST.getlist('tests'):
            exclusion_val = self.request.POST.get(f'exclusion_{test_id}', '')
            try:
                exclusion_amount = float(exclusion_val)
            except (ValueError, TypeError):
                continue
            SetpackageTest.objects.create(
                package=self.object,
                test_id=test_id,
                exclusion_amount=exclusion_amount
            )
        return redirect(self.success_url)


@method_decorator(login_required, name='dispatch')
class SetpackageDeleteView(DeleteView):
    model = Setpackage
    template_name = 'setpackages/setpackage_confirm_delete.html'
    success_url = reverse_lazy('setpackage_list')


@require_GET
@login_required
def get_available_transaction_purposes(request, company_id):
    purposes = (
        Setpackage.objects.filter(company_id=company_id)
        .values_list('package_transaction_purpose', flat=True)
        .distinct()
    )
    return JsonResponse({'purposes': list(purposes)})


@require_GET
@login_required
def get_tests_by_transaction_purpose(request, company_id, purpose):
    test_ids = (
        SetpackageTest.objects
        .filter(
            package__company_id=company_id,
            package__package_transaction_purpose=purpose
        )
        .values_list('test_id', flat=True)
        .distinct()
    )
    return JsonResponse({'test_ids': list(test_ids)})


@login_required
def get_package_price(request):
    purpose = request.GET.get("purpose")
    company_id = request.GET.get("company_id")
    try:
        package = Setpackage.objects.get(
            package_transaction_purpose=purpose,
            company_id=company_id
        )
        return JsonResponse({'promo_price': float(package.package_promo_price)})
    except Setpackage.DoesNotExist:
        return JsonResponse({'promo_price': None})
