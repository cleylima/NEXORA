from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from cadastros.models import (
    Empresa,
    Unidade,
    Setor,
    Funcionario,
)

@login_required
def dashboard(request):

    total_empresas = Empresa.objects.filter(
        ativo=True
    ).count()

    total_unidades = Unidade.objects.filter(
        ativo=True
    ).count()

    total_setores = Setor.objects.filter(
        ativo=True
    ).count()

    total_funcionarios = Funcionario.objects.filter(
        ativo=True
    ).count()

    funcionarios_com_lotacao_atual = (
        Funcionario.objects
        .filter(
            ativo=True,
            lotacoes__fim__isnull=True
        )
        .distinct()
        .count()
    )

    funcionarios_sem_lotacao = (
        total_funcionarios
        - funcionarios_com_lotacao_atual
    )

    contexto = {
        "total_empresas": total_empresas,
        "total_unidades": total_unidades,
        "total_setores": total_setores,
        "total_funcionarios": total_funcionarios,
        "funcionarios_sem_lotacao": funcionarios_sem_lotacao,
    }

    return render(
        request,
        "core/dashboard.html",
        contexto
    )