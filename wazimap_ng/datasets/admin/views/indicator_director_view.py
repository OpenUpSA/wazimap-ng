from ..forms.indicator_drector_admin_form import IndicatorDirectorForm
from django.views.generic.edit import FormView

class IndicatorDirectorAdminView(FormView):
    form_class = IndicatorDirectorForm
    template_name = 'admin/indicatordata_upload_director.html'
    success_url = '/admin/datasets/indicatordata/'

    def form_valid(self, form):
        json_data = form.cleaned_data['json_data']
        dataset = form.cleaned_data['dataset']

        # Error handling should come here


        form.process_json(dataset, json_data)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Manually plugging in context variables needed 
        # to display necessary links and blocks in the 
        # django admin. 
        context['title'] = 'Upload JSON Indicator Director File'
        context['site_header'] = ''
        context['has_permission'] = True

        return context