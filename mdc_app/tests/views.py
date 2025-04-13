# tests/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Test
from .forms import TestForm


@method_decorator(login_required, name='dispatch')
class TestListView(ListView):
    model = Test
    template_name = 'tests/test_list.html'
    context_object_name = 'tests'

@method_decorator(login_required, name='dispatch')
class TestDetailView(DetailView):
    model = Test
    template_name = 'tests/test_detail.html'
    context_object_name = 'test'

@method_decorator(login_required, name='dispatch')
class TestCreateView(CreateView):
    model = Test
    form_class = TestForm
    template_name = 'tests/test_form.html'
    success_url = reverse_lazy('test_new')

    def form_valid(self, form):
        data = form.cleaned_data
        existing_test = Test.objects.filter(
            test_name__iexact=data['test_name']
        ).first()

        if existing_test:
            # Pass this info to template context
            return self.render_to_response(self.get_context_data(
                form=form,
                existing_test=existing_test,
                show_modal=True,
                modal_message=f"Test already exists with ID {existing_test.id}"
            ))
        else:
            self.object = form.save()
            return self.render_to_response(self.get_context_data(
                form=self.get_form_class()(instance=self.object),
                new_test=self.object,
                show_modal=True,
                modal_message=f"New test created with ID {self.object.id}"
            ))

@method_decorator(login_required, name='dispatch')
class TestUpdateView(UpdateView):
    model = Test
    form_class = TestForm
    template_name = 'tests/test_form.html'
    success_url = reverse_lazy('test_list')

@method_decorator(login_required, name='dispatch')
class TestDeleteView(DeleteView):
    model = Test
    template_name = 'tests/test_confirm_delete.html'
    success_url = reverse_lazy('test_list')