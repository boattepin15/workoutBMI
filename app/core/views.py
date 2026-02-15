from django.views.generic import TemplateView, CreateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import BodyAnalysis
from .forms import BodyAnalysisForm

class HomeView(TemplateView):
    template_name = "home.html"


class BodyAnalysisCreateView(LoginRequiredMixin, CreateView):
    model = BodyAnalysis
    form_class = BodyAnalysisForm
    template_name = 'core/body_analysis_form.html'
    
    def get_success_url(self):
        return reverse_lazy('analysis_result', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save(commit=False)
        self.object.calculate_stats() # Calculate before saving final state
        # calculate_stats saves the model, so we might define it to not save, but here it saves.
        # Actually calculate_stats in my implementation calls self.save(). 
        # So we just need to make sure we don't save twice unnecessarily or cause issues.
        # Let's adjust: form.save(commit=False) gives instance. 
        # We fill user. Then call calculate_stats() which calculates AND saves.
        messages.success(self.request, "วิเคราะห์ข้อมูลเรียบร้อยแล้ว")
        return super().form_valid(form)

class BodyAnalysisDetailView(LoginRequiredMixin, DetailView):
    model = BodyAnalysis
    template_name = 'core/body_analysis_result.html'
    context_object_name = 'analysis'

class BodyAnalysisListView(LoginRequiredMixin, ListView):
    model = BodyAnalysis
    template_name = 'core/history.html'
    context_object_name = 'analyses'
    ordering = ['-created_at']

    def get_queryset(self):
        return BodyAnalysis.objects.filter(user=self.request.user).order_by('-created_at')
