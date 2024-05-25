import uuid
from typing import Iterable

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Disciplina(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=255, null=False)

    def __str__(self) -> str:
        return f'{self.nome}'


class Turma(models.Model):
    MATUTINO = 1
    VESPERTINO = 2
    NOTURNO = 3

    TURNO_CHOICES = (
        (MATUTINO, 'Matutino'),
        (VESPERTINO, 'Vespertino'),
        (NOTURNO, 'Noturno'),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=255, unique=True, null=False)
    turno = models.PositiveSmallIntegerField(choices=TURNO_CHOICES, blank=False, null=False)
    calendario = models.FileField(null=True, blank=True)

    disciplinas = models.ManyToManyField(Disciplina)

    def __str__(self) -> str:
        return f'{self.nome}'


class CustomUser(AbstractUser):
    ADMIN = 1
    ALUNO = 2

    ROLE_CHOICES = (
        (ALUNO, 'Aluno'),
        (ADMIN, 'Admin'),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length=255, unique=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True)
    password = models.CharField(max_length=255, blank=False, null=False)
    prev_password = models.CharField(max_length=255, blank=True, null=True)
    is_password_changed = models.BooleanField(default=False, blank=False, null=False)

    cpf = models.CharField(max_length=60, null=True)
    data_nascimento = models.DateField(null=True)

    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, null=True, blank=True)

    def set_password(self, raw_password: str | None) -> None:
        self.prev_password = raw_password
        self.is_password_changed = False

        return super().set_password(raw_password)
    
    def save(self, retype_password=False, force_insert: bool = ..., force_update: bool = ..., using: str | None = ..., update_fields: Iterable[str] | None = ..., *args, **kwargs) -> None:
        plain_text_password = self.prev_password

        if retype_password or self.is_superuser:
            self.is_password_changed = True
        
        self.prev_password = None

        super(CustomUser, self).save(*args, **kwargs)

        if retype_password: return


class CustomUserDisciplina(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    falta = models.IntegerField()
    nota = models.DecimalField(decimal_places=2, max_digits=5)


class Pendencias(models.Model):
    STATUS_AGUARDANDO = 1
    STATUS_RESOLVIDO = 2

    STATUS_CHOICES = (
        (STATUS_AGUARDANDO, 'Aguardando Resposta'),
        (STATUS_RESOLVIDO, 'Resolvido'),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=255)
    descricao = models.TextField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, blank=False, null=False, default=STATUS_AGUARDANDO)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
