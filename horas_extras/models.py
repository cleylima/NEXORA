from datetime import datetime, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from cadastros.models import (
    Funcionario,
    Setor,
)
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)


class CompetenciaHoraExtra(models.Model):

    class Status(models.TextChoices):
        ABERTA = "ABERTA", "Aberta"
        ENVIADA_RH = "ENVIADA_RH", "Enviada ao RH"
        EM_CONFERENCIA = "EM_CONFERENCIA", "Em conferência"
        DEVOLVIDA = "DEVOLVIDA", "Devolvida para correção"
        APROVADA = "APROVADA", "Aprovada"
        FECHADA = "FECHADA", "Fechada"
        
    enviada_rh_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="competencias_he_enviadas_rh",
        verbose_name="Enviada ao RH por"
    )

    enviada_rh_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Enviada ao RH em"
    )

    conferencia_iniciada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="competencias_he_conferidas",
        verbose_name="Conferência iniciada por"
    )

    conferencia_iniciada_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Conferência iniciada em"
    )

    aprovada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="competencias_he_aprovadas",
        verbose_name="Aprovada por"
    )

    aprovada_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Aprovada em"
    )

    fechada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="competencias_he_fechadas",
        verbose_name="Fechada por"
    )

    fechada_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fechada em"
    )

    ano = models.PositiveIntegerField(
        verbose_name="Ano"
    )

    mes = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12),
        ],
        verbose_name="Mês"
    )

    setor = models.ForeignKey(
        Setor,
        on_delete=models.PROTECT,
        related_name="competencias_horas_extras",
        verbose_name="Setor"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ABERTA,
        verbose_name="Status"
    )

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="competencias_horas_extras_criadas",
        verbose_name="Criado por"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Competência de Hora Extra"
        verbose_name_plural = "Competências de Horas Extras"

        ordering = [
            "-ano",
            "-mes",
            "setor__nome",
        ]

        permissions = [
            (
                "visualizar_horas_extras",
                "Pode visualizar horas extras"
            ),
            (
                "lancar_horas_extras",
                "Pode lançar horas extras"
            ),
            (
                "enviar_horas_extras_rh",
                "Pode enviar horas extras ao RH"
            ),
            (
                "conferir_horas_extras",
                "Pode conferir horas extras"
            ),
            (
                "aprovar_horas_extras",
                "Pode aprovar horas extras"
            ),
            (
                "devolver_horas_extras",
                "Pode devolver horas extras para correção"
            ),
            (
                "fechar_horas_extras",
                "Pode fechar horas extras"
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "ano",
                    "mes",
                    "setor",
                ],
                name="competencia_he_unica_por_setor",
                violation_error_message=(
                    "Já existe uma competência de horas extras "
                    "para este setor neste mês e ano."
                ),
            )
        ]

    def __str__(self):
        return (
            f"{self.setor.nome} - "
            f"{self.mes:02d}/{self.ano}"
        )
        
    


class HoraExtra(models.Model):

    competencia = models.ForeignKey(
        CompetenciaHoraExtra,
        on_delete=models.PROTECT,
        related_name="lancamentos",
        verbose_name="Competência"
    )

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        related_name="horas_extras",
        verbose_name="Funcionário"
    )

    data = models.DateField(
        verbose_name="Data"
    )

    hora_inicio = models.TimeField(
        verbose_name="Hora de início"
    )

    hora_fim = models.TimeField(
        verbose_name="Hora de término"
    )

    intervalo_minutos = models.PositiveIntegerField(
        default=0,
        verbose_name="Intervalo em minutos"
    )

    observacao = models.TextField(
        blank=True,
        verbose_name="Observação"
    )

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="horas_extras_criadas",
        verbose_name="Criado por"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Hora Extra"
        verbose_name_plural = "Horas Extras"

        ordering = [
            "-data",
            "funcionario__nome",
        ]

    def __str__(self):
        return (
            f"{self.funcionario.nome} - "
            f"{self.data:%d/%m/%Y}"
        )

    @property
    def duracao_minutos(self):

        inicio = datetime.combine(
            self.data,
            self.hora_inicio,
        )

        fim = datetime.combine(
            self.data,
            self.hora_fim,
        )

        if fim <= inicio:
            fim += timedelta(days=1)

        minutos = int(
            (fim - inicio).total_seconds() // 60
        )

        minutos -= self.intervalo_minutos or 0

        return max(minutos, 0)


    @property
    def duracao_horas(self):

        horas = self.duracao_minutos // 60
        minutos = self.duracao_minutos % 60

        return f"{horas:02d}:{minutos:02d}"

    def clean(self):

        super().clean()

        if not self.competencia_id:
            return

        if self.data.year != self.competencia.ano:
            raise ValidationError(
                {
                    "data":
                        "A data deve pertencer ao ano da competência."
                }
            )

        if self.data.month != self.competencia.mes:
            raise ValidationError(
                {
                    "data":
                        "A data deve pertencer ao mês da competência."
                }
            )

        if (
            self.competencia.status
            == CompetenciaHoraExtra.Status.FECHADA
        ):
            raise ValidationError(
                "Não é possível alterar uma competência fechada."
            )
            
class PendenciaHoraExtra(models.Model):

    hora_extra = models.ForeignKey(
        HoraExtra,
        on_delete=models.CASCADE,
        related_name="pendencias",
        verbose_name="Hora extra"
    )

    observacao = models.TextField(
        verbose_name="Observação do RH"
    )

    criada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pendencias_horas_extras_criadas",
        verbose_name="Criada por"
    )

    criada_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criada em"
    )

    resolvida = models.BooleanField(
        default=False,
        verbose_name="Resolvida"
    )

    resolvida_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="pendencias_horas_extras_resolvidas",
        verbose_name="Resolvida por"
    )

    resolvida_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Resolvida em"
    )

    class Meta:
        verbose_name = "Pendência de Hora Extra"
        verbose_name_plural = "Pendências de Horas Extras"

        ordering = [
            "-criada_em"
        ]

    def __str__(self):

        status = (
            "Resolvida"
            if self.resolvida
            else "Pendente"
        )

        return (
            f"{self.hora_extra.funcionario.nome} - "
            f"{self.hora_extra.data:%d/%m/%Y} - "
            f"{status}"
        )
            
class MovimentacaoCompetencia(models.Model):

    class Acao(models.TextChoices):
        CRIADA = "CRIADA", "Competência criada"
        ENVIADA_RH = "ENVIADA_RH", "Enviada ao RH"
        CONFERENCIA = "CONFERENCIA", "Conferência iniciada"
        APROVADA = "APROVADA", "Competência aprovada"
        DEVOLVIDA = "DEVOLVIDA", "Devolvida para correção"
        REENVIADA = "REENVIADA", "Reenviada ao RH"
        FECHADA = "FECHADA", "Competência fechada"

    competencia = models.ForeignKey(
        CompetenciaHoraExtra,
        on_delete=models.CASCADE,
        related_name="movimentacoes",
        verbose_name="Competência"
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimentacoes_competencias_he",
        verbose_name="Usuário"
    )

    acao = models.CharField(
        max_length=30,
        choices=Acao.choices,
        verbose_name="Ação"
    )

    observacao = models.TextField(
        blank=True,
        verbose_name="Observação"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Realizado em"
    )

    def __str__(self):
        return (
            f"{self.competencia} - "
            f"{self.get_acao_display()}"
        )

    class Meta:
        verbose_name = "Movimentação da Competência"
        verbose_name_plural = "Movimentações das Competências"
        ordering = ["-criado_em"]