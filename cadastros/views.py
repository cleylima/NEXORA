from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import timedelta

from .forms import EmpresaForm, UnidadeForm, SetorForm, FuncaoForm, TurnoForm, FuncionarioForm, LotacaoFuncionarioForm
from .models import Empresa, Unidade, Setor, Funcao, Turno, Funcionario, LotacaoFuncionario


@login_required
def listar_empresas(request):

    empresas = Empresa.objects.all()

    return render(
        request,
        "cadastros/empresas/listar.html",
        {
            "empresas": empresas
        }
    )


@login_required
def nova_empresa(request):

    if request.method == "POST":

        form = EmpresaForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect(
                "listar_empresas"
            )

    else:
        form = EmpresaForm()

    return render(
        request,
        "cadastros/empresas/form.html",
        {
            "form": form,
            "titulo": "Nova Empresa"
        }
    )


@login_required
def editar_empresa(request, pk):

    empresa = get_object_or_404(
        Empresa,
        pk=pk
    )

    if request.method == "POST":

        form = EmpresaForm(
            request.POST,
            instance=empresa
        )

        if form.is_valid():
            form.save()

            return redirect(
                "listar_empresas"
            )

    else:

        form = EmpresaForm(
            instance=empresa
        )

    return render(
        request,
        "cadastros/empresas/form.html",
        {
            "form": form,
            "titulo": "Editar Empresa"
        }
    )


@login_required
def listar_unidades(request):

    unidades = Unidade.objects.select_related(
        "empresa"
    )

    return render(
        request,
        "cadastros/unidades/listar.html",
        {
            "unidades": unidades
        }
    )


@login_required
def nova_unidade(request):

    if request.method == "POST":

        form = UnidadeForm(
            request.POST
        )

        if form.is_valid():
            form.save()

            return redirect(
                "listar_unidades"
            )

    else:
        form = UnidadeForm()

    return render(
        request,
        "cadastros/unidades/form.html",
        {
            "form": form,
            "titulo": "Nova Unidade"
        }
    )


@login_required
def editar_unidade(request, pk):

    unidade = get_object_or_404(
        Unidade,
        pk=pk
    )

    if request.method == "POST":

        form = UnidadeForm(
            request.POST,
            instance=unidade
        )

        if form.is_valid():
            form.save()

            return redirect(
                "listar_unidades"
            )

    else:

        form = UnidadeForm(
            instance=unidade
        )

    return render(
        request,
        "cadastros/unidades/form.html",
        {
            "form": form,
            "titulo": "Editar Unidade"
        }
    )

@login_required
def listar_setores(request):

    setores = Setor.objects.select_related(
        "unidade",
        "unidade__empresa"
    )

    return render(
        request,
        "cadastros/setores/listar.html",
        {
            "setores": setores
        }
    )


@login_required
def novo_setor(request):

    if request.method == "POST":

        form = SetorForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                "listar_setores"
            )

    else:

        form = SetorForm()

    return render(
        request,
        "cadastros/setores/form.html",
        {
            "form": form,
            "titulo": "Novo Setor"
        }
    )


@login_required
def editar_setor(request, pk):

    setor = get_object_or_404(
        Setor,
        pk=pk
    )

    if request.method == "POST":

        form = SetorForm(
            request.POST,
            instance=setor
        )

        if form.is_valid():

            form.save()

            return redirect(
                "listar_setores"
            )

    else:

        form = SetorForm(
            instance=setor
        )

    return render(
        request,
        "cadastros/setores/form.html",
        {
            "form": form,
            "titulo": "Editar Setor"
        }
    )
    
@login_required
def listar_funcoes(request):

    funcoes = Funcao.objects.all()

    return render(
        request,
        "cadastros/funcoes/listar.html",
        {
            "funcoes": funcoes
        }
    )


@login_required
def nova_funcao(request):

    if request.method == "POST":

        form = FuncaoForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                "listar_funcoes"
            )

    else:

        form = FuncaoForm()

    return render(
        request,
        "cadastros/funcoes/form.html",
        {
            "form": form,
            "titulo": "Nova Função"
        }
    )


@login_required
def editar_funcao(request, pk):

    funcao = get_object_or_404(
        Funcao,
        pk=pk
    )

    if request.method == "POST":

        form = FuncaoForm(
            request.POST,
            instance=funcao
        )

        if form.is_valid():

            form.save()

            return redirect(
                "listar_funcoes"
            )

    else:

        form = FuncaoForm(
            instance=funcao
        )

    return render(
        request,
        "cadastros/funcoes/form.html",
        {
            "form": form,
            "titulo": "Editar Função"
        }
    )
    
@login_required
def listar_turnos(request):

    turnos = Turno.objects.all()

    return render(
        request,
        "cadastros/turnos/listar.html",
        {
            "turnos": turnos
        }
    )


@login_required
def novo_turno(request):

    if request.method == "POST":

        form = TurnoForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                "listar_turnos"
            )

    else:

        form = TurnoForm()

    return render(
        request,
        "cadastros/turnos/form.html",
        {
            "form": form,
            "titulo": "Novo Turno"
        }
    )


@login_required
def editar_turno(request, pk):

    turno = get_object_or_404(
        Turno,
        pk=pk
    )

    if request.method == "POST":

        form = TurnoForm(
            request.POST,
            instance=turno
        )

        if form.is_valid():

            form.save()

            return redirect(
                "listar_turnos"
            )

    else:

        form = TurnoForm(
            instance=turno
        )

    return render(
        request,
        "cadastros/turnos/form.html",
        {
            "form": form,
            "titulo": "Editar Turno"
        }
    )
    
@login_required
def listar_funcionarios(request):

    funcionarios = (
        Funcionario.objects
        .all()
        .prefetch_related(
            "lotacoes__setor",
            "lotacoes__setor__unidade",
            "lotacoes__funcao",
            "lotacoes__turno",
        )
    )

    return render(
        request,
        "cadastros/funcionarios/listar.html",
        {
            "funcionarios": funcionarios
        }
    )


@login_required
def novo_funcionario(request):

    if request.method == "POST":

        form = FuncionarioForm(request.POST)

        if form.is_valid():

            funcionario = form.save()

            return redirect(
                "detalhar_funcionario",
                pk=funcionario.pk
            )

    else:

        form = FuncionarioForm()

    return render(
        request,
        "cadastros/funcionarios/form.html",
        {
            "form": form,
            "titulo": "Novo Funcionário"
        }
    )


@login_required
def editar_funcionario(request, pk):

    funcionario = get_object_or_404(
        Funcionario,
        pk=pk
    )

    if request.method == "POST":

        form = FuncionarioForm(
            request.POST,
            instance=funcionario
        )

        if form.is_valid():

            form.save()

            return redirect(
                "detalhar_funcionario",
                pk=funcionario.pk
            )

    else:

        form = FuncionarioForm(
            instance=funcionario
        )

    return render(
        request,
        "cadastros/funcionarios/form.html",
        {
            "form": form,
            "titulo": "Editar Funcionário"
        }
    )


@login_required
def detalhar_funcionario(request, pk):

    funcionario = get_object_or_404(
        Funcionario,
        pk=pk
    )

    lotacoes = (
        funcionario.lotacoes
        .select_related(
            "setor",
            "setor__unidade",
            "setor__unidade__empresa",
            "funcao",
            "turno"
        )
    )

    return render(
        request,
        "cadastros/funcionarios/detalhar.html",
        {
            "funcionario": funcionario,
            "lotacoes": lotacoes,
        }
    )

@login_required
def nova_lotacao_funcionario(request, pk):

    funcionario = get_object_or_404(
        Funcionario,
        pk=pk
    )

    if request.method == "POST":

        form = LotacaoFuncionarioForm(
            request.POST
        )

        if form.is_valid():

            nova_lotacao = form.save(
                commit=False
            )

            nova_lotacao.funcionario = funcionario

            lotacao_atual = (
                funcionario.lotacoes
                .filter(fim__isnull=True)
                .first()
            )

            if lotacao_atual:

                if nova_lotacao.inicio <= lotacao_atual.inicio:

                    form.add_error(
                        "inicio",
                        "A nova lotação deve iniciar após a lotação atual."
                    )

                else:

                    lotacao_atual.fim = (
                        nova_lotacao.inicio
                        - timedelta(days=1)
                    )

                    lotacao_atual.save()

                    nova_lotacao.save()

                    messages.success(
                        request,
                        "Nova lotação registrada com sucesso."
                    )

                    return redirect(
                        "detalhar_funcionario",
                        pk=funcionario.pk
                    )

            else:

                nova_lotacao.save()

                messages.success(
                    request,
                    "Lotação registrada com sucesso."
                )

                return redirect(
                    "detalhar_funcionario",
                    pk=funcionario.pk
                )

    else:

        form = LotacaoFuncionarioForm()

    return render(
        request,
        "cadastros/funcionarios/lotacao_form.html",
        {
            "form": form,
            "funcionario": funcionario,
        }
    )