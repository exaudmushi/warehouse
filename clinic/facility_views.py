from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Facility

class FacilityListView(ListView):
    model = Facility
    template_name = 'core/facilities/faicility_list.html'
    context_object_name = 'facilities'

class FacilityCreateView(CreateView):
    model = Facility
    template_name = 'core/facilities/facility_form.html'
    fields = ['name', 'ou']
    success_url = reverse_lazy('facility-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Facility created successfully!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Error creating facility. Ensure name and OU are unique.')
        return super().form_invalid(form)

class FacilityDetailView(DetailView):
    model = Facility
    template_name = 'core/facilities/facility_detail.html'
    context_object_name = 'facility'

class FacilityUpdateView(UpdateView):
    model = Facility
    template_name = 'core/facilities/facility_form.html'
    fields = ['name', 'ou']
    success_url = reverse_lazy('facility_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Facility updated successfully!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating facility. Ensure name and OU are unique.')
        return super().form_invalid(form)

class FacilityDeleteView(DeleteView):
    model = Facility
    template_name = 'core/facilities/facility_confirm_delete.html'
    success_url = reverse_lazy('facility_list')
    context_object_name = 'facility'

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, 'Facility deleted successfully!')
        return response