# setpackages/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Setpackage, SetpackageTest
from .forms import SetpackageForm
from tests.models import Test


@method_decorator(login_required, name='dispatch')
class SetpackageListView(ListView):
    model = Setpackage
    template_name = 'setpackages/setpackage_list.html'
    context_object_name = 'setpackages'


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
    success_url = reverse_lazy('setpackage_list')  # redirect to list after success

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tests'] = Test.objects.all()
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        existing_setpackage = Setpackage.objects.filter(
            package_name__iexact=data['package_name']
        ).first()

        if existing_setpackage:
            return self.render_to_response(self.get_context_data(
                form=form,
                existing_setpackage=existing_setpackage,
                show_modal=True,
                modal_message=f"Setpackage already exists with ID {existing_setpackage.id}"
            ))
        else:
            self.object = form.save()

            # Save related SetpackageTest entries
            tests = self.request.POST.getlist('tests')
            for test_id in tests:
                exclusion_field = f'exclusion_{test_id}'
                exclusion_value = self.request.POST.get(exclusion_field)
                if exclusion_value:
                    try:
                        exclusion_amount = float(exclusion_value)
                        SetpackageTest.objects.create(
                            package=self.object,
                            test_id=test_id,
                            exclusion_amount=exclusion_amount
                        )
                    except ValueError:
                        continue  # skip if the value isn't a valid number

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
        
        # Attach exclusion info to test objects for the template
        for test in all_tests:
            test.is_checked = test.id in existing_tests
            test.exclusion_amount = existing_tests.get(test.id, "")
        
        context['tests'] = all_tests
        return context

    def form_valid(self, form):
        self.object = form.save()

        # Clear existing test associations
        self.object.tests.all().delete()

        # Add updated test associations
        tests = self.request.POST.getlist('tests')
        for test_id in tests:
            exclusion_value = self.request.POST.get(f'exclusion_{test_id}')
            if exclusion_value:
                try:
                    exclusion_amount = float(exclusion_value)
                    SetpackageTest.objects.create(
                        package=self.object,
                        test_id=test_id,
                        exclusion_amount=exclusion_amount
                    )
                except ValueError:
                    continue  # skip invalid input

        return redirect(self.success_url)



@method_decorator(login_required, name='dispatch')
class SetpackageDeleteView(DeleteView):
    model = Setpackage
    template_name = 'setpackages/setpackage_confirm_delete.html'
    success_url = reverse_lazy('setpackage_list')
