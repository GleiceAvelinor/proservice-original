from django.urls import path
from .views import EmpresaSignUpView, PortalAcessoView, EmpresaAtivarView

app_name = "signup"

urlpatterns = [
    path("", EmpresaSignUpView.as_view(), name="signup"),
    path("acessar/", PortalAcessoView.as_view(), name="portal_acesso"),
    path("ativar/<uuid:token>/", EmpresaAtivarView.as_view(), name="ativar_empresa"),
]