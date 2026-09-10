from django.db import models


class Empresa(models.Model):
    razao_social = models.CharField(
        max_length=200,
        verbose_name="Razão Social"
    )

    nome_fantasia = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nome Fantasia"
    )

    cnpj = models.CharField(
        max_length=18,
        unique=True,
        verbose_name="CNPJ"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.nome_fantasia or self.razao_social

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["razao_social"]


class Unidade(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name="unidades",
        verbose_name="Empresa"
    )

    nome = models.CharField(
        max_length=150,
        verbose_name="Nome da Unidade"
    )

    codigo = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Código"
    )

    cidade = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Cidade"
    )

    uf = models.CharField(
        max_length=2,
        blank=True,
        verbose_name="UF"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.empresa} - {self.nome}"

    class Meta:
        verbose_name = "Unidade"
        verbose_name_plural = "Unidades"
        ordering = ["empresa", "nome"]
        
class Setor(models.Model):
    unidade = models.ForeignKey(
        Unidade,
        on_delete=models.PROTECT,
        related_name="setores",
        verbose_name="Unidade"
    )

    nome = models.CharField(
        max_length=150,
        verbose_name="Nome do Setor"
    )

    codigo = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Código"
    )

    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.nome} - {self.unidade.nome}"

    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"
        ordering = ["unidade", "nome"]

        constraints = [
            models.UniqueConstraint(
                fields=["unidade", "nome"],
                name="setor_nome_unico_por_unidade"
            )
        ]
        
        
class Funcao(models.Model):
    nome = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Nome da Função"
    )

    codigo = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Código"
    )

    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Função"
        verbose_name_plural = "Funções"
        ordering = ["nome"]
        
class Turno(models.Model):
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome do Turno"
    )

    hora_inicio = models.TimeField(
        verbose_name="Hora de Início"
    )

    hora_fim = models.TimeField(
        verbose_name="Hora de Fim"
    )

    descricao = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descrição"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        ordering = ["nome"]
        
class Funcionario(models.Model):
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome completo"
    )

    matricula = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Matrícula"
    )

    cpf = models.CharField(
        max_length=14,
        blank=True,
        verbose_name="CPF"
    )

    data_admissao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de admissão"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.nome

    @property
    def lotacao_atual(self):
        return (
            self.lotacoes
            .filter(fim__isnull=True)
            .select_related(
                "setor",
                "setor__unidade",
                "funcao",
                "turno"
            )
            .first()
        )

    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"
        ordering = ["nome"]


class LotacaoFuncionario(models.Model):
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        related_name="lotacoes",
        verbose_name="Funcionário"
    )

    setor = models.ForeignKey(
        Setor,
        on_delete=models.PROTECT,
        related_name="lotacoes",
        verbose_name="Setor"
    )

    funcao = models.ForeignKey(
        Funcao,
        on_delete=models.PROTECT,
        related_name="lotacoes",
        verbose_name="Função"
    )

    turno = models.ForeignKey(
        Turno,
        on_delete=models.PROTECT,
        related_name="lotacoes",
        null=True,
        blank=True,
        verbose_name="Turno"
    )

    inicio = models.DateField(
        verbose_name="Data de início"
    )

    fim = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de término"
    )

    observacao = models.TextField(
        blank=True,
        verbose_name="Observação"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.funcionario} - {self.setor}"

    class Meta:
        verbose_name = "Lotação do Funcionário"
        verbose_name_plural = "Lotações dos Funcionários"
        ordering = ["-inicio"]
        
        
class LiderancaSetor(models.Model):
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        related_name="liderancas",
        verbose_name="Líder"
    )

    setor = models.ForeignKey(
        Setor,
        on_delete=models.PROTECT,
        related_name="liderancas",
        verbose_name="Setor"
    )

    inicio = models.DateField(
        verbose_name="Início"
    )

    fim = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fim"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.funcionario.nome} - {self.setor.nome}"

    @property
    def ativa(self):
        from django.utils import timezone

        hoje = timezone.localdate()

        return (
            self.inicio <= hoje
            and (
                self.fim is None
                or self.fim >= hoje
            )
        )

    def clean(self):
        super().clean()

        from django.core.exceptions import ValidationError

        if self.fim and self.fim < self.inicio:
            raise ValidationError({
                "fim": "A data de término não pode ser anterior à data de início."
            })

    class Meta:
        verbose_name = "Liderança de Setor"
        verbose_name_plural = "Lideranças de Setores"
        ordering = [
            "setor__nome",
            "funcionario__nome",
        ]