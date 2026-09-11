from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.listar_competencias,
        name="listar_competencias_he"
    ),

    path(
        "nova/",
        views.nova_competencia,
        name="nova_competencia_he"
    ),

    path(
        "<int:pk>/funcionarios/",
        views.funcionarios_competencia,
        name="funcionarios_competencia_he"
    ),

    path(
        "<int:pk>/lancamentos/novo/",
        views.nova_hora_extra,
        name="nova_hora_extra"
    ),

    path(
        "lancamentos/<int:pk>/editar/",
        views.editar_hora_extra,
        name="editar_hora_extra"
    ),

    path(
        "lancamentos/<int:pk>/excluir/",
        views.excluir_hora_extra,
        name="excluir_hora_extra"
    ),
    
    path(
        "<int:pk>/enviar-rh/",
        views.enviar_competencia_rh,
        name="enviar_competencia_rh"
    ),

    path(
        "<int:pk>/iniciar-conferencia/",
        views.iniciar_conferencia_competencia,
        name="iniciar_conferencia_competencia"
    ),

    path(
        "<int:pk>/aprovar/",
        views.aprovar_competencia,
        name="aprovar_competencia"
    ),

    path(
        "<int:pk>/fechar/",
        views.fechar_competencia,
        name="fechar_competencia"
    ),

    path(
        "<int:pk>/editar/",
        views.editar_competencia,
        name="editar_competencia_he"
    ),

    path(
        "<int:pk>/excluir/",
        views.excluir_competencia,
        name="excluir_competencia_he"
    ),
    
    path(
        "<int:pk>/devolver/",
        views.devolver_competencia,
        name="devolver_competencia"
    ),

    path(
        "<int:pk>/",
        views.detalhar_competencia,
        name="detalhar_competencia_he"
    ),

]