from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from urllib.parse import urlencode

EXEMPT_PREFIXES = (
    "/accounts/login/",
    "/accounts/logout/",
    "/admin/",
    "/accounts/password_reset/",
    "/accounts/reset/",
    "/accounts/password_reset_done/",
    "/accounts/reset/done/",
)

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if request.user.is_authenticated:
            return self.get_response(request)

        # Allow exempt paths
        if any(path.startswith(p) for p in EXEMPT_PREFIXES):
            return self.get_response(request)

        # Redirect to login with ?next=
        login_url = settings.LOGIN_URL
        query = urlencode({"next": path})
        return redirect(f"{login_url}?{query}")
