from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    nome = models.CharField(
        max_length=150,
        verbose_name="Nome completo"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    funcionario = models.OneToOneField(
        "cadastros.Funcionario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuario",
        verbose_name="Funcionário vinculado"
    )

    def __str__(self):
        return self.nome or self.username

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"