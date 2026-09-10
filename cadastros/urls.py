from django.urls import path

from . import views


urlpatterns = [

    # Empresas

    path(
        "empresas/",
        views.listar_empresas,
        name="listar_empresas"
    ),

    path(
        "empresas/nova/",
        views.nova_empresa,
        name="nova_empresa"
    ),

    path(
        "empresas/<int:pk>/editar/",
        views.editar_empresa,
        name="editar_empresa"
    ),


    # Unidades

    path(
        "unidades/",
        views.listar_unidades,
        name="listar_unidades"
    ),

    path(
        "unidades/nova/",
        views.nova_unidade,
        name="nova_unidade"
    ),

    path(
        "unidades/<int:pk>/editar/",
        views.editar_unidade,
        name="editar_unidade"
    ),
        # Setores

    path(
        "setores/",
        views.listar_setores,
        name="listar_setores"
    ),

    path(
        "setores/novo/",
        views.novo_setor,
        name="novo_setor"
    ),

    path(
        "setores/<int:pk>/editar/",
        views.editar_setor,
        name="editar_setor"
    ),
    
    # Funções

    path(
        "funcoes/",
        views.listar_funcoes,
        name="listar_funcoes"
    ),

    path(
        "funcoes/nova/",
        views.nova_funcao,
        name="nova_funcao"
    ),

    path(
        "funcoes/<int:pk>/editar/",
        views.editar_funcao,
        name="editar_funcao"
    ),
    
    # Turnos

    path(
        "turnos/",
        views.listar_turnos,
        name="listar_turnos"
    ),

    path(
        "turnos/novo/",
        views.novo_turno,
        name="novo_turno"
    ),

    path(
        "turnos/<int:pk>/editar/",
        views.editar_turno,
        name="editar_turno"
    ),
    
    # Funcionários

    path(
        "funcionarios/",
        views.listar_funcionarios,
        name="listar_funcionarios"
    ),

    path(
        "funcionarios/novo/",
        views.novo_funcionario,
        name="novo_funcionario"
    ),

    path(
        "funcionarios/<int:pk>/",
        views.detalhar_funcionario,
        name="detalhar_funcionario"
    ),

    path(
        "funcionarios/<int:pk>/editar/",
        views.editar_funcionario,
        name="editar_funcionario"
    ),

    path(
        "funcionarios/<int:pk>/lotacao/nova/",
        views.nova_lotacao_funcionario,
        name="nova_lotacao_funcionario"
    ),

]