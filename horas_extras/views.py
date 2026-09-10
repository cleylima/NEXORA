from datetime import date
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from cadastros.models import Funcionario
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
from horas_extras.permissoes import setores_acessiveis_por



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

    if request.method == "POST":

        form = CompetenciaHoraExtraForm(
            request.POST
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
def detalhar_competencia(request, pk):

    competencia = get_object_or_404(
        CompetenciaHoraExtra.objects.select_related(
            "setor",
            "setor__unidade",
            "setor__unidade__empresa",
            "criado_por",
        ),
        pk=pk
    )

    lancamentos = (
        competencia.lancamentos
        .select_related("funcionario", "criado_por")
        .order_by(
            "data",
            "funcionario__nome"
        )
    )

    competencia.nome_mes = MESES.get(
        competencia.mes,
        str(competencia.mes)
    )

    return render(
        request,
        "horas_extras/competencias/detalhar.html",
        {
            "competencia": competencia,
            "lancamentos": lancamentos,
        }
    )
    
@login_required
def nova_hora_extra(request, pk):

    competencia = get_object_or_404(
        CompetenciaHoraExtra.objects.select_related(
            "setor",
            "setor__unidade",
        ),
        pk=pk
    )

    if competencia.status not in [
        CompetenciaHoraExtra.Status.ABERTA,
        CompetenciaHoraExtra.Status.DEVOLVIDA,
    ]:
        messages.error(
            request,
            "Os lançamentos desta competência não podem ser alterados."
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
                "Hora extra lançada com sucesso."
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
            "titulo": "Lançar Hora Extra",
        }
    )
    
@login_required
def funcionarios_competencia(request, pk):

    competencia = get_object_or_404(
        CompetenciaHoraExtra.objects.select_related(
            "setor"
        ),
        pk=pk
    )

    data = request.GET.get("data")

    if not data:
        return JsonResponse(
            {
                "funcionarios": []
            }
        )

    try:
        data = date.fromisoformat(data)

    except ValueError:
        return JsonResponse(
            {
                "funcionarios": []
            },
            status=400
        )

    # A data precisa pertencer à competência
    if (
        data.year != competencia.ano
        or data.month != competencia.mes
    ):
        return JsonResponse(
            {
                "funcionarios": [],
                "erro": (
                    "A data não pertence "
                    "à competência selecionada."
                ),
            },
            status=400
        )

    funcionarios = (
        Funcionario.objects
        .filter(
            ativo=True,
            lotacoes__setor=competencia.setor,
            lotacoes__inicio__lte=data,
        )
        .filter(
            Q(lotacoes__fim__isnull=True)
            |
            Q(lotacoes__fim__gte=data)
        )
        .distinct()
        .order_by("nome")
    )

    dados = [
        {
            "id": funcionario.pk,
            "nome": funcionario.nome,
            "matricula": funcionario.matricula,
        }
        for funcionario in funcionarios
    ]

    return JsonResponse(
        {
            "funcionarios": dados
        }
    )
    
@login_required
def editar_hora_extra(request, pk):

    hora_extra = get_object_or_404(
        HoraExtra.objects.select_related(
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
            "Os lançamentos desta competência não podem ser alterados."
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
                "Lançamento atualizado com sucesso."
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
            "titulo": "Editar Hora Extra",
            "hora_extra": hora_extra,
        }
    )
    
@login_required
def excluir_hora_extra(request, pk):

    hora_extra = get_object_or_404(
        HoraExtra.objects.select_related(
            "competencia",
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
            "Os lançamentos desta competência não podem ser alterados."
        )

        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    if request.method == "POST":

        hora_extra.delete()

        messages.success(
            request,
            "Lançamento excluído com sucesso."
        )

        return redirect(
            "detalhar_competencia_he",
            pk=competencia.pk
        )

    return redirect(
        "detalhar_competencia_he",
        pk=competencia.pk
    )
    
@login_required
def enviar_competencia_rh(request, pk):

    competencia = get_object_or_404(
        CompetenciaHoraExtra,
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
            "Somente competências abertas podem ser enviadas ao RH."
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
        if competencia.movimentacoes.filter(
            acao=MovimentacaoCompetencia.Acao.DEVOLVIDA
        ).exists()
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

    competencia = get_object_or_404(
        CompetenciaHoraExtra,
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

    competencia = get_object_or_404(
        CompetenciaHoraExtra,
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

    competencia = get_object_or_404(
        CompetenciaHoraExtra,
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

    competencia = get_object_or_404(
        CompetenciaHoraExtra,
        pk=pk
    )

    if (
        competencia.status
        != CompetenciaHoraExtra.Status.EM_CONFERENCIA
    ):
        messages.error(
            request,
            "Somente competências em conferência podem ser devolvidas."
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