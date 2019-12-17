# from django.http import JsonResponse
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
#
# from user.forms import CustomUserCreationForm
# from django.urls import reverse_lazy, reverse
# from django.views.generic import CreateView, FormView
#
# # auth
# from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView
# from django.contrib.auth.decorators import login_required
#
#
# class SignUpView(CreateView):
#     form_class = CustomUserCreationForm
#     success_url = reverse_lazy('FLEX:login')
#     template_name = 'flexart/index_register.html'
#
#     # model object
#     context_object_name = 'signup_model'
#
#     context_form_name = 'signup_form'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         # to change form in context of template
#
#         # A
#         # context[self.context_form_name] = self.get_form()
#         # del context['form']
#         # B
#         context[self.context_form_name] = context.pop('form')
#         return context
#
#
# class CustomLoginView(LoginView):
#     template_name = 'flexart/index_login.html'
#     extra_context = {'next': reverse_lazy('FLEX:index')}
#
#
# @method_decorator(login_required(login_url=reverse_lazy('FLEX:login')), name='dispatch', )
# class CustomPasswordChangeView(PasswordChangeView):
#     template_name = 'flexart/index_password_change_form.html'
#     success_url = reverse_lazy('FLEX:password_change_done')
#
#
# @method_decorator(login_required(login_url=reverse_lazy('FLEX:login')), name='dispatch', )
# class CustomPasswordChangeDoneView(PasswordChangeDoneView):
#     template_name = 'flexart/index_password_change_done.html'
