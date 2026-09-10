from django import forms

from .models import Empresa, Unidade, Setor, Funcao, Turno, Funcionario, LotacaoFuncionario


class EmpresaForm(forms.ModelForm):

    class Meta:
        model = Empresa

        fields = [
            "razao_social",
            "nome_fantasia",
            "cnpj",
            "ativo",
        ]

        widgets = {
            "razao_social": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Razão social da empresa"
                }
            ),

            "nome_fantasia": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome fantasia"
                }
            ),

            "cnpj": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "00.000.000/0000-00"
                }
            ),

            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }


class UnidadeForm(forms.ModelForm):

    class Meta:
        model = Unidade

        fields = [
            "empresa",
            "nome",
            "codigo",
            "cidade",
            "uf",
            "ativo",
        ]

        widgets = {
            "empresa": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome da unidade"
                }
            ),

            "codigo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Código interno"
                }
            ),

            "cidade": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "uf": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": "2"
                }
            ),

            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }
        
class SetorForm(forms.ModelForm):

    class Meta:
        model = Setor

        fields = [
            "unidade",
            "nome",
            "codigo",
            "descricao",
            "ativo",
        ]

        widgets = {
            "unidade": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome do setor"
                }
            ),

            "codigo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Código interno"
                }
            ),

            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descrição do setor",
                    "rows": 4
                }
            ),

            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }

class FuncaoForm(forms.ModelForm):

    class Meta:
        model = Funcao

        fields = [
            "nome",
            "codigo",
            "descricao",
            "ativo",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome da função"
                }
            ),

            "codigo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Código interno"
                }
            ),

            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descrição da função",
                    "rows": 4
                }
            ),

            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }
        
class TurnoForm(forms.ModelForm):

    class Meta:
        model = Turno

        fields = [
            "nome",
            "hora_inicio",
            "hora_fim",
            "descricao",
            "ativo",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome do turno"
                }
            ),

            "hora_inicio": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time"
                },
                format="%H:%M"
            ),

            "hora_fim": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time"
                },
                format="%H:%M"
            ),

            "descricao": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Turno da manhã"
                }
            ),

            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }
        
class FuncionarioForm(forms.ModelForm):

    class Meta:
        model = Funcionario

        fields = [
            "nome",
            "matricula",
            "cpf",
            "data_admissao",
            "ativo",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome completo"
                }
            ),

            "matricula": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Matrícula"
                }
            ),

            "cpf": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "000.000.000-00"
                }
            ),

            "data_admissao": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                },
                format="%Y-%m-%d"
            ),

            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }


class LotacaoFuncionarioForm(forms.ModelForm):

    class Meta:
        model = LotacaoFuncionario

        fields = [
            "setor",
            "funcao",
            "turno",
            "inicio",
            "observacao",
        ]

        widgets = {
            "setor": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "funcao": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "turno": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "inicio": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                },
                format="%Y-%m-%d"
            ),

            "observacao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observação opcional"
                }
            ),
        }