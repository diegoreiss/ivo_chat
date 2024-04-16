# Generated by Django 5.0.3 on 2024-04-15 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='cpf',
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='data_nascimento',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='prev_password',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(2, 'Aluno'), (1, 'Admin')], null=True),
        ),
    ]