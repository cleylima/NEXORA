from datetime import date, datetime
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Q
from django.db import transaction
from cadastros.models import LotacaoFuncionario
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import (
    CompetenciaHoraExtraForm,
    HoraExtraForm,
    HoraExtraFormSet,
    DevolverCompetenciaForm,
)
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

    # =========================================================
    # PERMISSÃO
    # =========================================================

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

        return redirect("dashboard")


    # =========================================================
    # SETORES ACESSÍVEIS
    # =========================================================

    setores_acessiveis = setores_acessiveis_por(
        request.user
    )


    # =========================================================
    # QUERY BASE
    # =========================================================

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
    )


    # =========================================================
    # FILTROS RECEBIDOS PELA URL
    # =========================================================

    status = request.GET.get("status")
    setor_id = request.GET.get("setor")
    ano = request.GET.get("ano")
    mes = request.GET.get("mes")


    if status:
        competencias = competencias.filter(
            status=status
        )

    if setor_id:
        competencias = competencias.filter(
            setor_id=setor_id
        )

    if ano:
        competencias = competencias.filter(
            ano=ano
        )

    if mes:
        competencias = competencias.filter(
            mes=mes
        )


    # =========================================================
    # ORDENAÇÃO
    # =========================================================

    competencias = competencias.order_by(
        "-ano",
        "-mes",
        "setor__nome",
    )


    # =========================================================
    # RESUMO POR STATUS
    # Sempre considera apenas setores acessíveis ao usuário.
    # =========================================================

    resumo = (
        CompetenciaHoraExtra.objects
        .filter(
            setor__in=setores_acessiveis
        )
        .aggregate(

            abertas=Count(
                "id",
                filter=Q(
                    status=CompetenciaHoraExtra.Status.ABERTA
                )
            ),

            enviadas_rh=Count(
                "id",
                filter=Q(
                    status=CompetenciaHoraExtra.Status.ENVIADA_RH
                )
            ),

            em_conferencia=Count(
                "id",
                filter=Q(
                    status=CompetenciaHoraExtra.Status.EM_CONFERENCIA
                )
            ),

            devolvidas=Count(
                "id",
                filter=Q(
                    status=CompetenciaHoraExtra.Status.DEVOLVIDA
                )
            ),

            aprovadas=Count(
                "id",
                filter=Q(
                    status=CompetenciaHoraExtra.Status.APROVADA
                )
            ),

            fechadas=Count(
                "id",
                filter=Q(
                    status=CompetenciaHoraExtra.Status.FECHADA
                )
            ),
        )
    )
    
    # =========================================================
    # PENDÊNCIAS DO USUÁRIO
    # =========================================================

    status_pendentes = []

    # Líder:
    # competências devolvidas pelo RH precisam de correção.
    if (
        request.user.has_perm(
            "horas_extras.lancar_horas_extras"
        )
        or request.user.is_superuser
    ):
        status_pendentes.append(
            CompetenciaHoraExtra.Status.DEVOLVIDA
        )


    # RH:
    # competências que aguardam alguma ação do fluxo.
    if (
        request.user.has_perm(
            "horas_extras.conferir_horas_extras"
        )
        or request.user.is_superuser
    ):
        status_pendentes.extend([
            CompetenciaHoraExtra.Status.ENVIADA_RH,
            CompetenciaHoraExtra.Status.EM_CONFERENCIA,
        ])


    # Competências aprovadas ainda precisam ser fechadas.
    if (
        request.user.has_perm(
            "horas_extras.fechar_horas_extras"
        )
        or request.user.is_superuser
    ):
        status_pendentes.append(
            CompetenciaHoraExtra.Status.APROVADA
        )


    pendencias_usuario = (
        CompetenciaHoraExtra.objects
        .filter(
            setor__in=setores_acessiveis,
            status__in=status_pendentes,
        )
        .select_related(
            "setor",
            "setor__unidade",
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


    # =========================================================
    # ANOS DISPONÍVEIS
    # =========================================================

    anos_disponiveis = (
        CompetenciaHoraExtra.objects
        .filter(
            setor__in=setores_acessiveis
        )
        .values_list(
            "ano",
            flat=True
        )
        .distinct()
        .order_by("-ano")
    )


    # =========================================================
    # MESES
    # =========================================================

    meses = [
        (1, "Janeiro"),
        (2, "Fevereiro"),
        (3, "Março"),
        (4, "Abril"),
        (5, "Maio"),
        (6, "Junho"),
        (7, "Julho"),
        (8, "Agosto"),
        (9, "Setembro"),
        (10, "Outubro"),
        (11, "Novembro"),
        (12, "Dezembro"),
    ]


    # =========================================================
    # NOME DO MÊS NAS PENDÊNCIAS
    # =========================================================

    nomes_meses = dict(meses)

    for competencia in pendencias_usuario:
        competencia.nome_mes_exibicao = nomes_meses.get(
            competencia.mes,
            ""
        )


    contexto = {

        "competencias": competencias,
        "setores": setores_acessiveis,
        "anos_disponiveis": anos_disponiveis,
        "meses": meses,
        "status_choices": (
            CompetenciaHoraExtra.Status.choices
        ),
        "resumo": resumo,
        "pendencias_usuario": pendencias_usuario,
        "total_pendencias": pendencias_usuario.count(),

        # Mantém os filtros selecionados
        "filtro_status": status or "",
        "filtro_setor": setor_id or "",
        "filtro_ano": ano or "",
        "filtro_mes": mes or "",
    }


    return render(
        request,
        "horas_extras/competencias/listar.html",
        contexto,
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


    # =========================================================
    # RESUMO DA COMPETÊNCIA
    # =========================================================

    total_lancamentos = lancamentos.count()


    total_funcionarios = (
        lancamentos
        .values("funcionario_id")
        .distinct()
        .count()
    )


    total_minutos = sum(
        lancamento.duracao_minutos
        for lancamento in lancamentos
    )


    total_horas = total_minutos // 60
    minutos_restantes = total_minutos % 60


    total_horas_formatado = (
        f"{total_horas:02d}:{minutos_restantes:02d}"
    )


    # =========================================================
    # RESUMO POR FUNCIONÁRIO
    # =========================================================

    resumo_por_funcionario = {}


    for lancamento in lancamentos:

        funcionario_id = lancamento.funcionario_id


        if funcionario_id not in resumo_por_funcionario:

            resumo_por_funcionario[funcionario_id] = {
                "funcionario": lancamento.funcionario,
                "lancamentos": 0,
                "total_minutos": 0,
            }


        resumo_por_funcionario[funcionario_id][
            "lancamentos"
        ] += 1


        resumo_por_funcionario[funcionario_id][
            "total_minutos"
        ] += lancamento.duracao_minutos


    # =========================================================
    # FORMATA TOTAL POR FUNCIONÁRIO
    # =========================================================

    for item in resumo_por_funcionario.values():

        horas = item["total_minutos"] // 60
        minutos = item["total_minutos"] % 60

        item["total_horas"] = (
            f"{horas:02d}:{minutos:02d}"
        )


    resumo_funcionarios = sorted(
        resumo_por_funcionario.values(),
        key=lambda item: item["funcionario"].nome.lower()
    )


    # =========================================================
    # NOME DO MÊS
    # =========================================================

    competencia.nome_mes = MESES.get(
        competencia.mes,
        str(competencia.mes)
    )


    # =========================================================
    # HISTÓRICO
    # =========================================================

    movimentacoes = (
        competencia.movimentacoes
        .select_related("usuario")
        .all()
    )


    # =========================================================
    # CONTEXTO
    # =========================================================

    contexto = {

        "competencia": competencia,

        "lancamentos": lancamentos,

        "movimentacoes": movimentacoes,

        "resumo_competencia": {
            "funcionarios": total_funcionarios,
            "lancamentos": total_lancamentos,
            "total_horas": total_horas_formatado,
        },

        "resumo_funcionarios": resumo_funcionarios,
    }


    return render(
        request,
        "horas_extras/competencias/detalhar.html",
        contexto,
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

    data_lote = None
    data_lote_str = ""

    if request.method == "POST":

        data_lote_str = request.POST.get(
            "data_lote",
            ""
        ).strip()

        if data_lote_str:

            try:
                data_lote = datetime.strptime(
                    data_lote_str,
                    "%Y-%m-%d"
                ).date()

            except ValueError:
                data_lote = None



    if request.method == "POST":

        formset = HoraExtraFormSet(
            request.POST,
            prefix="horas",
            form_kwargs={
                "competencia": competencia,
                "data_lote": data_lote,
            }
        )


        erro_data = None

        if not data_lote:
            erro_data = (
                "Informe uma data válida para os lançamentos."
            )

        elif (
            data_lote.month != competencia.mes
            or data_lote.year != competencia.ano
        ):
            erro_data = (
                "A data deve pertencer à competência selecionada."
            )
            
        if (
            not erro_data
            and formset.is_valid()
        ):

            formularios_validos = [
                form
                for form in formset.forms
                if form.cleaned_data
                and not form.cleaned_data.get("DELETE")
                and form.cleaned_data.get("funcionario")
            ]

            if not formularios_validos:

                messages.error(
                    request,
                    "Adicione pelo menos um funcionário."
                )

            else:

                with transaction.atomic():

                    for form in formularios_validos:

                        hora_extra = form.save(
                            commit=False
                        )

                        hora_extra.competencia = competencia
                        hora_extra.data = data_lote
                        hora_extra.criado_por = request.user

                        hora_extra.save()

                quantidade = len(
                    formularios_validos
                )

                messages.success(
                    request,
                    (
                        f"{quantidade} lançamento"
                        f"{'s' if quantidade != 1 else ''} "
                        "de hora extra registrado"
                        f"{'s' if quantidade != 1 else ''} "
                        "com sucesso."
                    )
                )

                return redirect(
                    "detalhar_competencia_he",
                    pk=competencia.pk
                )

    else:

        formset = HoraExtraFormSet(
            prefix="horas",
            form_kwargs={
                "competencia": competencia,
                "data_lote": None,
            }
        )

        erro_data = None


    return render(
        request,
        "horas_extras/lancamentos/lote.html",
        {
            "formset": formset,
            "competencia": competencia,
            "titulo": "Lançar Horas Extras",
            "data_lote": data_lote_str,
            "erro_data": erro_data,
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