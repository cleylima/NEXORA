from datetime import date, datetime
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from cadastros.models import LotacaoFuncionario
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CompetenciaHoraExtraForm, HoraExtraForm, DevolverCompetenciaForm
from .models import (
    CompetenciaHoraExtra,
    HoraExtra,
    MovimentacaoCompetencia
)
from .permissoes import setores_acessiveis_por



MESES = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


@login_required
def listar_competencias(request):

    if not request.user.has_perm(
        "horas_extras.visualizar_horas_extras"
    ) and not request.user.is_superuser:
        messages.error(
            request,
            "Você não possui permissão para visualizar horas extras."
        )
        return redirect("dashboard")

    setores_acessiveis = setores_acessiveis_por(
        request.user
    )

    competencias = (
        CompetenciaHoraExtra.objects
        .filter(
            setor__in=setores_acessiveis
        )
        .select_related(
            "setor",
            "setor__unidade",
            "setor__unidade__empresa",
            "criado_por",
        )
        .annotate(
            total_lancamentos=Count("lancamentos")
        )
        .order_by(
            "-ano",
            "-mes",
            "setor__nome",
        )
    )

    for competencia in competencias:
        competencia.nome_mes = MESES.get(
            competencia.mes,
            str(competencia.mes)
        )

    return render(
        request,
        "horas_extras/competencias/listar.html",
        {
            "competencias": competencias,
        }
    )


@login_required
def nova_competencia(request):

    if (
        not request.user.has_perm(
            "horas_extras.lancar_horas_extras"
        )
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "Você não possui permissão para criar competências de horas extras."
        )

        return redirect(
            "listar_competencias_he"
        )

    if request.method == "POST":

        form = CompetenciaHoraExtraForm(
            request.POST,
            usuario=request.user,
        )

        if form.is_valid():

            competencia = form.save(
                commit=False
            )

            competencia.criado_por = request.user

            competencia.save()

            MovimentacaoCompetencia.objects.create(
                competencia=competencia,
                usuario=request.user,
                acao=MovimentacaoCompetencia.Acao.CRIADA,
            )

            messages.success(
                request,
                "Competência criada com sucesso."
            )

            return redirect(
                "detalhar_competencia_he",
                pk=competencia.pk
            )

    else:

        hoje = date.today()

        form = CompetenciaHoraExtraForm(
            usuario=request.user,
            initial={
                "mes": hoje.month,
                "ano": hoje.year,
            }
        )

    return render(
        request,
        "horas_extras/competencias/form.html",
        {
            "form": form,
            "titulo": "Nova Competência",
        }
    )

@login_required
def editar_competencia(request, pk):

    if (
        not request.user.has_perm(
            "horas_extras.lancar_horas_extras"
        )
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "Você não possui permissão para editar competências."
        )
        return redirect(
            "listar_competencias_he"
        )

    setores_acessiveis = setores_acessiveis_por(
        request.user
    )

    competencia = get_object_or_404(
        CompetenciaHoraExtra.objects.filter(
            setor__in=setores_acessiveis
        ),
        pk=pk
    )

    if competencia.status != CompetenciaHoraExtra.Status.ABERTA:
        messages.error(
            request,
            "Somente competências abertas podem ser editadas."
        )
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    if competencia.lancamentos.exists():
        messages.error(
            request,
            "Não é possível editar uma competência que já possui lançamentos."
        )
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    if request.method == "POST":

        form = CompetenciaHoraExtraForm(
            request.POST,
            instance=competencia,
            usuario=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Competência atualizada com sucesso."
            )

            return redirect(
                "detalhar_competencia_he",
                pk=competencia.pk
            )

    else:

        form = CompetenciaHoraExtraForm(
            instance=competencia,
            usuario=request.user,
        )

    return render(
        request,
        "horas_extras/competencias/form.html",
        {
            "form": form,
            "competencia": competencia,
            "titulo": "Editar Competência",
            "modo_edicao": True,
        }
    )


@login_required
def excluir_competencia(request, pk):

    if (
        not request.user.has_perm(
            "horas_extras.lancar_horas_extras"
        )
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "Você não possui permissão para excluir competências."
        )
        return redirect(
            "listar_competencias_he"
        )

    setores_acessiveis = setores_acessiveis_por(
        request.user
    )

    competencia = get_object_or_404(
        CompetenciaHoraExtra.objects.filter(
            setor__in=setores_acessiveis
        ),
        pk=pk
    )

    if competencia.status != CompetenciaHoraExtra.Status.ABERTA:
        messages.error(
            request,
            "Somente competências abertas podem ser excluídas."
        )
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    if competencia.lancamentos.exists():
        messages.error(
            request,
            "Não é possível excluir uma competência que já possui lançamentos."
        )
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    if request.method != "POST":
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    competencia.delete()

    messages.success(
        request,
        "Competência excluída com sucesso."
    )

    return redirect(
        "listar_competencias_he"
    )


@login_required
def detalhar_competencia(request, pk):

    if (
        not request.user.has_perm(
            "horas_extras.visualizar_horas_extras"
        )
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "Você não possui permissão para visualizar horas extras."
        )

        return redirect(
            "listar_competencias_he"
        )

    setores_acessiveis = setores_acessiveis_por(
        request.user
    )

    competencia = get_object_or_404(
        CompetenciaHoraExtra.objects
        .filter(
            setor__in=setores_acessiveis
        )
        .select_related(
            "setor",
            "setor__unidade",
            "setor__unidade__empresa",
            "criado_por",
        ),
        pk=pk
    )

    lancamentos = (
        competencia.lancamentos
        .select_related(
            "funcionario",
            "criado_por"
        )
        .order_by(
            "data",
            "funcionario__nome"
        )
    )

    competencia.nome_mes = MESES.get(
        competencia.mes,
        str(competencia.mes)
    )

    movimentacoes = (
        competencia.movimentacoes
        .select_related("usuario")
        .all()
    )

    return render(
        request,
        "horas_extras/competencias/detalhar.html",
        {
            "competencia": competencia,
            "lancamentos": lancamentos,
            "movimentacoes": movimentacoes,
        }
    )
    
@login_required
def nova_hora_extra(request, pk):

    if (
        not request.user.has_perm(
            "horas_extras.lancar_horas_extras"
        )
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "Você não possui permissão para lançar horas extras."
        )
        return redirect(
            "listar_competencias_he"
        )

    setores_acessiveis = setores_acessiveis_por(
        request.user
    )

    competencia = get_object_or_404(
        CompetenciaHoraExtra.objects
        .filter(
            setor__in=setores_acessiveis
        )
        .select_related(
            "setor",
            "setor__unidade",
            "setor__unidade__empresa",
        ),
        pk=pk
    )

    if competencia.status not in [
        CompetenciaHoraExtra.Status.ABERTA,
        CompetenciaHoraExtra.Status.DEVOLVIDA,
    ]:
        messages.error(
            request,
            "Não é possível lançar horas extras nesta competência."
        )
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    if request.method == "POST":

        form = HoraExtraForm(
            request.POST,
            competencia=competencia,
        )

        if form.is_valid():

            hora_extra = form.save(
                commit=False
            )

            hora_extra.competencia = competencia
            hora_extra.criado_por = request.user

            hora_extra.save()

            messages.success(
                request,
                "Hora extra registrada com sucesso."
            )

            return redirect(
                "detalhar_competencia_he",
                pk=competencia.pk
            )

    else:

        form = HoraExtraForm(
            competencia=competencia
        )

    return render(
        request,
        "horas_extras/lancamentos/form.html",
        {
            "form": form,
            "competencia": competencia,
            "titulo": "Nova Hora Extra",
        }
    )
      
@login_required
def funcionarios_competencia(request, pk):

    # O usuário precisa, no mínimo, ter acesso ao módulo.
    if (
        not request.user.has_perm(
            "horas_extras.visualizar_horas_extras"
        )
        and not request.user.has_perm(
            "horas_extras.lancar_horas_extras"
        )
        and not request.user.is_superuser
    ):
        return JsonResponse(
            {
                "erro": "Você não possui permissão para acessar esta competência."
            },
            status=403,
        )

    setores_acessiveis = setores_acessiveis_por(
        request.user
    )

    # Além da permissão, a competência precisa pertencer
    # a um setor acessível ao usuário.
    competencia = get_object_or_404(
        CompetenciaHoraExtra.objects.select_related(
            "setor"
        ).filter(
            setor__in=setores_acessiveis
        ),
        pk=pk,
    )

    data_str = request.GET.get("data")

    if not data_str:
        return JsonResponse(
            {"funcionarios": []}
        )

    try:
        data = datetime.strptime(
            data_str,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        return JsonResponse(
            {"funcionarios": []},
            status=400,
        )

    lotacoes = (
        LotacaoFuncionario.objects
        .filter(
            setor=competencia.setor,
            inicio__lte=data,
        )
        .filter(
            Q(fim__isnull=True) |
            Q(fim__gte=data)
        )
        .select_related(
            "funcionario"
        )
        .order_by(
            "funcionario__nome"
        )
    )

    funcionarios = [
        {
            "id": lotacao.funcionario.id,
            "nome": lotacao.funcionario.nome,
        }
        for lotacao in lotacoes
    ]

    return JsonResponse(
        {
            "funcionarios": funcionarios
        }
    )
    
@login_required
def editar_hora_extra(request, pk):

    if (
        not request.user.has_perm(
            "horas_extras.lancar_horas_extras"
        )
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "Você não possui permissão para editar horas extras."
        )
        return redirect(
            "listar_competencias_he"
        )

    setores_acessiveis = setores_acessiveis_por(
        request.user
    )

    hora_extra = get_object_or_404(
        HoraExtra.objects
        .filter(
            competencia__setor__in=setores_acessiveis
        )
        .select_related(
            "competencia",
            "competencia__setor",
            "competencia__setor__unidade",
            "funcionario",
        ),
        pk=pk
    )

    competencia = hora_extra.competencia

    if competencia.status not in [
        CompetenciaHoraExtra.Status.ABERTA,
        CompetenciaHoraExtra.Status.DEVOLVIDA,
    ]:
        messages.error(
            request,
            "Não é possível editar lançamentos nesta competência."
        )
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    if request.method == "POST":

        form = HoraExtraForm(
            request.POST,
            instance=hora_extra,
            competencia=competencia,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Hora extra atualizada com sucesso."
            )

            return redirect(
                "detalhar_competencia_he",
                pk=competencia.pk
            )

    else:

        form = HoraExtraForm(
            instance=hora_extra,
            competencia=competencia,
        )

    return render(
        request,
        "horas_extras/lancamentos/form.html",
        {
            "form": form,
            "competencia": competencia,
            "hora_extra": hora_extra,
            "titulo": "Editar Hora Extra",
        }
    )
    
@login_required
def excluir_hora_extra(request, pk):

    if (
        not request.user.has_perm(
            "horas_extras.lancar_horas_extras"
        )
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "Você não possui permissão para excluir horas extras."
        )
        return redirect(
            "listar_competencias_he"
        )

    setores_acessiveis = setores_acessiveis_por(
        request.user
    )

    hora_extra = get_object_or_404(
        HoraExtra.objects
        .filter(
            competencia__setor__in=setores_acessiveis
        )
        .select_related(
            "competencia",
            "competencia__setor",
        ),
        pk=pk
    )

    competencia = hora_extra.competencia

    if competencia.status not in [
        CompetenciaHoraExtra.Status.ABERTA,
        CompetenciaHoraExtra.Status.DEVOLVIDA,
    ]:
        messages.error(
            request,
            "Não é possível excluir lançamentos nesta competência."
        )
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    if request.method == "POST":

        hora_extra.delete()

        messages.success(
            request,
            "Hora extra excluída com sucesso."
        )

    return redirect(
        "detalhar_competencia_he",
        pk=competencia.pk
    )
    
@login_required
def enviar_competencia_rh(request, pk):

    if (
        not request.user.has_perm(
            "horas_extras.enviar_horas_extras_rh"
        )
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "Você não possui permissão para enviar competências ao RH."
        )
        return redirect(
            "listar_competencias_he"
        )

    setores_acessiveis = setores_acessiveis_por(
        request.user
    )

    competencia = get_object_or_404(
        CompetenciaHoraExtra.objects
        .filter(
            setor__in=setores_acessiveis
        ),
        pk=pk
    )

    if request.method != "POST":
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    if competencia.status not in [
        CompetenciaHoraExtra.Status.ABERTA,
        CompetenciaHoraExtra.Status.DEVOLVIDA,
    ]:
        messages.error(
            request,
            "Somente competências abertas ou devolvidas podem ser enviadas ao RH."
        )

        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    if not competencia.lancamentos.exists():
        messages.error(
            request,
            "Não é possível enviar ao RH uma competência sem lançamentos."
        )

        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    status_anterior = competencia.status

    competencia.status = (
        CompetenciaHoraExtra.Status.ENVIADA_RH
    )

    competencia.enviada_rh_por = request.user
    competencia.enviada_rh_em = timezone.now()

    competencia.save(
        update_fields=[
            "status",
            "enviada_rh_por",
            "enviada_rh_em",
            "atualizado_em",
        ]
    )

    acao = (
        MovimentacaoCompetencia.Acao.REENVIADA
        if status_anterior
        == CompetenciaHoraExtra.Status.DEVOLVIDA
        else MovimentacaoCompetencia.Acao.ENVIADA_RH
    )

    MovimentacaoCompetencia.objects.create(
        competencia=competencia,
        usuario=request.user,
        acao=acao,
    )

    messages.success(
        request,
        "Competência enviada ao RH com sucesso."
    )

    return redirect(
        "detalhar_competencia_he",
        pk=competencia.pk
    )
    
@login_required
def iniciar_conferencia_competencia(request, pk):

    if (
        not request.user.has_perm(
            "horas_extras.conferir_horas_extras"
        )
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "Você não possui permissão para iniciar a conferência."
        )
        return redirect(
            "listar_competencias_he"
        )

    setores_acessiveis = setores_acessiveis_por(
        request.user
    )

    competencia = get_object_or_404(
        CompetenciaHoraExtra.objects.filter(
            setor__in=setores_acessiveis
        ),
        pk=pk
    )

    if request.method != "POST":
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    if (
        competencia.status
        != CompetenciaHoraExtra.Status.ENVIADA_RH
    ):
        messages.error(
            request,
            "Esta competência não está aguardando conferência."
        )
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    competencia.status = (
        CompetenciaHoraExtra.Status.EM_CONFERENCIA
    )

    competencia.conferencia_iniciada_por = request.user
    competencia.conferencia_iniciada_em = timezone.now()

    competencia.save(
        update_fields=[
            "status",
            "conferencia_iniciada_por",
            "conferencia_iniciada_em",
            "atualizado_em",
        ]
    )

    MovimentacaoCompetencia.objects.create(
        competencia=competencia,
        usuario=request.user,
        acao=MovimentacaoCompetencia.Acao.CONFERENCIA,
    )

    messages.success(
        request,
        "Conferência iniciada."
    )

    return redirect(
        "detalhar_competencia_he",
        pk=competencia.pk
    )
    
@login_required
def aprovar_competencia(request, pk):

    if (
        not request.user.has_perm(
            "horas_extras.aprovar_horas_extras"
        )
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "Você não possui permissão para aprovar competências."
        )
        return redirect(
            "listar_competencias_he"
        )

    setores_acessiveis = setores_acessiveis_por(
        request.user
    )

    competencia = get_object_or_404(
        CompetenciaHoraExtra.objects.filter(
            setor__in=setores_acessiveis
        ),
        pk=pk
    )

    if request.method != "POST":
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    if (
        competencia.status
        != CompetenciaHoraExtra.Status.EM_CONFERENCIA
    ):
        messages.error(
            request,
            "Somente competências em conferência podem ser aprovadas."
        )
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    competencia.status = (
        CompetenciaHoraExtra.Status.APROVADA
    )

    competencia.aprovada_por = request.user
    competencia.aprovada_em = timezone.now()

    competencia.save(
        update_fields=[
            "status",
            "aprovada_por",
            "aprovada_em",
            "atualizado_em",
        ]
    )

    MovimentacaoCompetencia.objects.create(
        competencia=competencia,
        usuario=request.user,
        acao=MovimentacaoCompetencia.Acao.APROVADA,
    )

    messages.success(
        request,
        "Competência aprovada com sucesso."
    )

    return redirect(
        "detalhar_competencia_he",
        pk=competencia.pk
    )
    
@login_required
def fechar_competencia(request, pk):

    if (
        not request.user.has_perm(
            "horas_extras.fechar_horas_extras"
        )
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "Você não possui permissão para fechar competências."
        )
        return redirect(
            "listar_competencias_he"
        )

    setores_acessiveis = setores_acessiveis_por(
        request.user
    )

    competencia = get_object_or_404(
        CompetenciaHoraExtra.objects.filter(
            setor__in=setores_acessiveis
        ),
        pk=pk
    )

    if request.method != "POST":
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    if (
        competencia.status
        != CompetenciaHoraExtra.Status.APROVADA
    ):
        messages.error(
            request,
            "Somente competências aprovadas podem ser fechadas."
        )
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    competencia.status = (
        CompetenciaHoraExtra.Status.FECHADA
    )

    competencia.fechada_por = request.user
    competencia.fechada_em = timezone.now()

    competencia.save(
        update_fields=[
            "status",
            "fechada_por",
            "fechada_em",
            "atualizado_em",
        ]
    )

    MovimentacaoCompetencia.objects.create(
        competencia=competencia,
        usuario=request.user,
        acao=MovimentacaoCompetencia.Acao.FECHADA,
    )

    messages.success(
        request,
        "Competência fechada com sucesso."
    )

    return redirect(
        "detalhar_competencia_he",
        pk=competencia.pk
    )

@login_required
def devolver_competencia(request, pk):

    if (
        not request.user.has_perm(
            "horas_extras.devolver_horas_extras"
        )
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "Você não possui permissão para devolver competências."
        )
        return redirect(
            "listar_competencias_he"
        )

    setores_acessiveis = setores_acessiveis_por(
        request.user
    )

    competencia = get_object_or_404(
        CompetenciaHoraExtra.objects.filter(
            setor__in=setores_acessiveis
        ),
        pk=pk
    )

    if competencia.status not in [
        CompetenciaHoraExtra.Status.EM_CONFERENCIA,
        CompetenciaHoraExtra.Status.APROVADA,
    ]:
        messages.error(
            request,
            "Somente competências em conferência ou aprovadas podem ser devolvidas."
        )

        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    if request.method != "POST":
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    form = DevolverCompetenciaForm(
        request.POST
    )

    if not form.is_valid():
        messages.error(
            request,
            "Informe o motivo da devolução."
        )
        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    competencia.status = (
        CompetenciaHoraExtra.Status.DEVOLVIDA
    )

    competencia.save(
        update_fields=[
            "status",
            "atualizado_em",
        ]
    )

    MovimentacaoCompetencia.objects.create(
        competencia=competencia,
        usuario=request.user,
        acao=MovimentacaoCompetencia.Acao.DEVOLVIDA,
        observacao=form.cleaned_data["motivo"],
    )

    messages.success(
        request,
        "Competência devolvida para correção."
    )

    return redirect(
        "detalhar_competencia_he",
        pk=competencia.pk
    )