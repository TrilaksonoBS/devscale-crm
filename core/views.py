from django.contrib.auth.mixins import LoginRequiredMixin


class LoginRequiredMixinView(LoginRequiredMixin):
    login_url = "/accounts/login/"
    redirect_field_name = "next"

    class Meta:
        abstract = True
