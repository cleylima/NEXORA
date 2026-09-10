from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Nexora", {
            "fields": (
                "nome",
                "ativo",
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Nexora", {
            "fields": (
                "nome",
                "ativo",
            )
        }),
    )

    list_display = (
        "username",
        "nome",
        "email",
        "is_staff",
        "ativo",
    )

    search_fields = (
        "username",
        "nome",
        "email",
    )