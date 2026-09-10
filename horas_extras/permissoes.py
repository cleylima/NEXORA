from django.db.models import Q
from django.utils import timezone

from cadastros.models import Setor


def setores_liderados_por(usuario):
    """
    Retorna os setores atualmente liderados pelo usuário.
    """

    if not usuario.is_authenticated:
        return Setor.objects.none()

    if not getattr(usuario, "funcionario_id", None):
        return Setor.objects.none()

    hoje = timezone.localdate()

    return (
        Setor.objects.filter(
            liderancas__funcionario=usuario.funcionario,
            liderancas__inicio__lte=hoje,
        )
        .filter(
            Q(liderancas__fim__isnull=True)
            | Q(liderancas__fim__gte=hoje)
        )
        .distinct()
    )


def setores_acessiveis_por(usuario):
    """
    Retorna os setores que o usuário pode acessar
    no módulo de Horas Extras.
    """

    if not usuario.is_authenticated:
        return Setor.objects.none()

    if usuario.is_superuser:
        return Setor.objects.all()

    if usuario.groups.filter(name="RH").exists():
        return Setor.objects.all()

    if usuario.groups.filter(name="Líder").exists():
        return setores_liderados_por(usuario)

    return Setor.objects.none()