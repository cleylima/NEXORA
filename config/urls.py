from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("core.urls")),
    path("usuarios/", include("usuarios.urls")),
    path("cadastros/", include("cadastros.urls")),
    path(
        "gestao-pessoas/horas-extras/",
        include("horas_extras.urls")
    ),
]