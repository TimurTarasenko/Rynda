# -*- coding: utf-8 -*-

from django.shortcuts import redirect, render_to_response
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic.detail import DetailView

from core.views import RyndaFormView, RyndaListView
from core.backends import IonAuth
from users.forms import (
    SimpleRegistrationForm,
    ForgotPasswordForm,
    ResetPasswordForm)
from users.models import create_new_user


class UserDetail(DetailView):
    model = User
    template_name = 'user_profile.html'
    context_object_name = 'u'


class UserList(RyndaListView):
    template_name = 'userlist.html'
    context_object_name = 'users'
    queryset = User.objects.select_related().filter(is_active=True).order_by('date_joined')
    paginator_url = '/user/page/'
    paginate_by = 10


class CreateUser(RyndaFormView):
    '''
    New user regiatration.
    If registration form is valid, create a new deactivated user,
    new user profile (via signal) and send activation email to user.
    '''
    template_name = 'registerform_simple.html'
    form_class = SimpleRegistrationForm
    success_url = '/'

    def form_valid(self, form):
        ce = form.cleaned_data
        create_new_user(
            first_name=ce['first_name'],
            last_name=ce['last_name'],
            email=ce['email'],
            password=ce['password1'],
        )
        return redirect(self.success_url)


class ForgotPassword(RyndaFormView):
    template_name = 'forgotpassword_form.html'
    form_class = ForgotPasswordForm
    success_url = '/'

    def form_valid(self, form):
        user = User.objects.get(email=form.cleaned_data['email'])
        auth = IonAuth()
        profile = user.get_profile()
        profile.forgotCode = auth.generate_code()
        profile.save()
        send_templated_email([user], 'emails/forgot_password',
            {
             'user': user,
             'forgot_code': profile.forgotCode,
             'site_url': self.request.META['SERVER_NAME'],
            }
        )
        messages.success(self.request,
            "На указанный адрес почты отправлено письмо с инструкциями")
        return redirect(self.success_url)


class ResetPassword(RyndaFormView):
    template_name = 'resetpassword_form.html'
    form_class = ResetPasswordForm
    success_url = '/'

    def form_valid(self, form):
        profile = Users.objects.get(forgotCode=form.cleaned_data['code'])
        user = profile.user
        profile.forgotCode = ''
        auth = IonAuth()
        passwd = auth.generate_code()[:6]
        user.password = auth.password_hash(passwd)
        profile.save()
        user.save()
        send_templated_email([user], 'emails/new_password',
            {'user': user, 'password': passwd,
            'base_url': self.request.META['SERVER_NAME'],
            }
        )
        return redirect(self.success_url)

def activate_profile(request, pk, key):
    user = User.objects.get(id=pk)
    p = user.get_profile()
    if p.activCode == key:
        user.is_active = True
        user.save()
        p.activCode = ''
        p.save()
        redirect('/login')
    redirect('/')
