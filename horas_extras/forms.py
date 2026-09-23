from django import forms
from django.db.models import Q

from cadastros.models import Funcionario
from .models import HoraExtra
from .permissoes import setores_acessiveis_por
from .models import CompetenciaHoraExtra


MESES = [
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


class CompetenciaHoraExtraForm(forms.ModelForm):

    mes = forms.TypedChoiceField(
        choices=MESES,
        coerce=int,
        label="Mês",
    )

    class Meta:

        model = CompetenciaHoraExtra

        fields = [
            "setor",
            "mes",
            "ano",
        ]

        widgets = {

            "setor": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "ano": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 2020,
                    "max": 2100,
                }
            ),

        }

    def __init__(self, *args, usuario=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.usuario = usuario
        
        self.fields["setor"].empty_label = "Selecione o setor"

        self.fields["mes"].widget.attrs.update(
            {
                "class": "form-select",
            }
        )

        if usuario is None:
            self.fields["setor"].queryset = (
                self.fields["setor"]
                .queryset
                .none()
            )

            return

        setores_acessiveis = setores_acessiveis_por(
            usuario
        )

        self.fields["setor"].queryset = (
            setores_acessiveis
            .filter(
                ativo=True
            )
            .select_related(
                "unidade",
                "unidade__empresa"
            )
            .order_by(
                "unidade__empresa__razao_social",
                "unidade__nome",
                "nome",
            )
        )

class HoraExtraForm(forms.ModelForm):
    class Meta:
        model = HoraExtra

        fields = [
            "funcionario",
            "data",
            "hora_inicio",
            "hora_fim",
            "intervalo_minutos",
            "observacao",
        ]

        widgets = {
            "funcionario": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "data": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),

            "hora_inicio": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                },
                format="%H:%M",
            ),

            "hora_fim": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                },
                format="%H:%M",
            ),

            "intervalo_minutos": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "step": 1,
                }
            ),

            "observacao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Informe uma observação, se necessário.",
                }
            ),
        }

    def __init__(
        self,
        *args,
        competencia=None,
        data_lote=None,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        self.competencia = competencia
        self.data_lote = data_lote

        self.fields["funcionario"].queryset = (
            Funcionario.objects.none()
        )
        self.fields["funcionario"].empty_label = (
            "Selecione uma data"
        )
        
        if data_lote:

            self.fields["data"].required = False

            self.fields["data"].widget = (
                forms.HiddenInput()
            )

            self.fields["data"].initial = data_lote

        if not competencia:
            return

        data_informada = self.data_lote

        if not data_informada:

            if self.is_bound:
                data_informada = self.data.get(
                    self.add_prefix("data")
                )

            elif self.instance and self.instance.pk:
                data_informada = self.instance.data

        if not data_informada:
            return

        if isinstance(data_informada, str):

            try:
                from datetime import datetime

                data_informada = datetime.strptime(
                    data_informada,
                    "%Y-%m-%d"
                ).date()

            except ValueError:
                return

        self.fields["funcionario"].queryset = (
            Funcionario.objects
            .filter(
                ativo=True,
                lotacoes__setor=competencia.setor,
                lotacoes__inicio__lte=data_informada,
            )
            .filter(
                Q(
                    lotacoes__fim__isnull=True
                )
                |
                Q(
                    lotacoes__fim__gte=data_informada
                )
            )
            .distinct()
            .order_by("nome")
        )

    def clean(self):

        cleaned_data = super().clean()

        if not self.competencia:
            return cleaned_data
        
        data = (
            self.data_lote
            or cleaned_data.get("data")
        )

        if self.data_lote:
            cleaned_data["data"] = self.data_lote
        funcionario = cleaned_data.get("funcionario")
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fim = cleaned_data.get("hora_fim")
        intervalo = cleaned_data.get(
            "intervalo_minutos"
        ) or 0

        if data:

            if (
                data.month != self.competencia.mes
                or data.year != self.competencia.ano
            ):

                self.add_error(
                    "data",
                    "A data deve pertencer à competência selecionada."
                )

        if data and funcionario:

            lotacao_valida = (
                funcionario.lotacoes
                .filter(
                    setor=self.competencia.setor,
                    inicio__lte=data,
                )
                .filter(
                    Q(fim__isnull=True)
                    |
                    Q(fim__gte=data)
                )
                .exists()
            )

            if not lotacao_valida:

                self.add_error(
                    "funcionario",
                    "O funcionário não estava lotado neste setor na data informada."
                )

        if (
            data
            and hora_inicio
            and hora_fim
        ):

            from datetime import datetime, timedelta

            inicio = datetime.combine(
                data,
                hora_inicio
            )

            fim = datetime.combine(
                data,
                hora_fim
            )

            if fim <= inicio:
                fim += timedelta(days=1)

            total_minutos = int(
                (fim - inicio).total_seconds() / 60
            )

            if intervalo >= total_minutos:

                self.add_error(
                    "intervalo_minutos",
                    "O intervalo não pode ser igual ou superior ao período trabalhado."
                )

        return cleaned_data

class BaseHoraExtraFormSet(forms.BaseFormSet):

    def clean(self):

        super().clean()

        if any(self.errors):
            return

        funcionarios_selecionados = set()

        for form in self.forms:

            if not form.cleaned_data:
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            funcionario = form.cleaned_data.get(
                "funcionario"
            )

            if not funcionario:
                continue

            if funcionario.pk in funcionarios_selecionados:

                form.add_error(
                    "funcionario",
                    (
                        "Este funcionário já foi "
                        "adicionado neste lançamento."
                    )
                )

            funcionarios_selecionados.add(
                funcionario.pk
            )


HoraExtraFormSet = forms.formset_factory(
    HoraExtraForm,
    formset=BaseHoraExtraFormSet,
    extra=1,
    can_delete=True,
)
    
class DevolverCompetenciaForm(forms.Form):

    motivo = forms.CharField(
        label="Motivo da devolução",
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": (
                    "Informe o que precisa ser corrigido "
                    "antes do reenvio ao RH."
                ),
            }
        )
    )

    def clean_motivo(self):

        motivo = self.cleaned_data["motivo"].strip()

        if len(motivo) < 5:
            raise forms.ValidationError(
                "Informe um motivo mais detalhado para a devolução."
            )

        return motivo