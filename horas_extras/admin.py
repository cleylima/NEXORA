from django.contrib import admin

from .models import (
    CompetenciaHoraExtra,
    HoraExtra,
)


@admin.register(CompetenciaHoraExtra)
class CompetenciaHoraExtraAdmin(admin.ModelAdmin):

    list_display = (
        "setor",
        "mes",
        "ano",
        "status",
        "criado_por",
    )

    list_filter = (
        "status",
        "ano",
        "mes",
        "setor",
    )

    search_fields = (
        "setor__nome",
    )


@admin.register(HoraExtra)
class HoraExtraAdmin(admin.ModelAdmin):

    list_display = (
        "funcionario",
        "data",
        "hora_inicio",
        "hora_fim",
        "duracao_horas",
        "competencia",
    )

    list_filter = (
        "data",
        "competencia__setor",
        "competencia__status",
    )

    search_fields = (
        "funcionario__nome",
        "funcionario__matricula",
    )