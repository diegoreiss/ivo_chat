from io import BytesIO
from datetime import datetime
from typing import Dict, Text, Any

from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4


def gerar_atestado_de_matricula(dados_atestado: Dict[Text, Dict[Text, Any]]) -> BytesIO:
    buffer = BytesIO()

    cnv = canvas.Canvas(buffer, pagesize=A4)

    cnv.drawString(50, 800, f'{"="*70}')
    cnv.drawString(220, 775, f'ATESTADO DE MATRÍCULA')
    cnv.drawString(50, 750, f'{"="*70}')

    cnv.drawString(50, 700, f'Eu, {dados_atestado["coordenador"]["nome"]}, Coordenador(a) da {dados_atestado["instituicao"]["nome"]},')
    cnv.drawString(50, 683, f'localizada na {dados_atestado["instituicao"]["endereco"]}, atesto que:')

    cnv.drawString(50, 650, f'Nome do Aluno(a): {dados_atestado["aluno"]["nome"]}')
    cnv.drawString(50, 633, f'Matrícula: {dados_atestado["aluno"]["matricula"]}')
    cnv.drawString(50, 616, f'Turma: {dados_atestado["aluno"]["turma"]}')
    
    
    cnv.drawString(50, 566, 'Encontra-se regularmente matriculado(a) nesta instituição, frequentando')
    cnv.drawString(50, 549, 'assiduamente as aulas.')

    now = datetime.now().strftime('%d/%m/%Y')

    cnv.drawString(50, 516, f'Emitido em: {now}')

    cnv.drawString(50, 466, f'{"="*70}')
    cnv.drawString(50, 449, f'{dados_atestado["coordenador"]["nome"]}')
    cnv.drawString(50, 432, f'{dados_atestado["coordenador"]["contato"]}')
    cnv.drawString(50, 415, f'{"="*70}')

    cnv.save()

    buffer.seek(0)

    return buffer


def gerar_atestado_de_frequencia(dados_atestado: Dict[Text, Dict[Text, Any]]) -> BytesIO:
    buffer = BytesIO()

    cnv = canvas.Canvas(buffer, pagesize=A4)

    cnv.drawString(50, 800, f'{"="*70}')
    cnv.drawString(220, 775, f'ATESTADO DE FREQUÊNCIA')
    cnv.drawString(50, 750, f'{"="*70}')

    cnv.drawString(50, 700, f'Eu, {dados_atestado["coordenador"]["nome"]}, Coordenador(a) da {dados_atestado["instituicao"]["nome"]},')
    cnv.drawString(50, 683, f'localizada na {dados_atestado["instituicao"]["endereco"]}, atesto que:')

    cnv.drawString(50, 650, f'Nome do Aluno(a): {dados_atestado["aluno"]["nome"]}')
    cnv.drawString(50, 633, f'Matrícula: {dados_atestado["aluno"]["matricula"]}')
    cnv.drawString(50, 616, f'Turma: {dados_atestado["aluno"]["turma"]}')
    
    
    ano_atual = datetime.now().year
    periodo_inicio = datetime(ano_atual, 2, 10).strftime('%d/%m/%Y')
    periodo_fim = datetime(ano_atual, 11, 25).strftime('%d/%m/%Y')
    cnv.drawString(50, 566, f'Frequentou regularmente as aulas no período de {periodo_inicio} a {periodo_fim}')

    now = datetime.now().strftime('%d/%m/%Y')

    cnv.drawString(50, 516, f'Emitido em: {now}')

    cnv.drawString(50, 466, f'{"="*70}')
    cnv.drawString(50, 449, f'{dados_atestado["coordenador"]["nome"]}')
    cnv.drawString(50, 432, f'{dados_atestado["coordenador"]["contato"]}')
    cnv.drawString(50, 415, f'{"="*70}')

    cnv.save()

    buffer.seek(0)

    return buffer


def gerar_historico_escolar(dados_historico):
    buffer = BytesIO()
    cnv = canvas.Canvas(buffer, pagesize=A4)

    cnv.drawString(50, 800, f'{"="*70}')
    cnv.drawString(225, 775, f'HISTÓRICO ESCOLAR')
    cnv.drawString(50, 750, f'{"="*70}')
    cnv.drawString(50, 700, f'Nome do Aluno(a): {dados_historico['aluno']['nome']}')
    cnv.drawString(50, 683, f'Matrícula: {dados_historico['aluno']['matricula']}')
    cnv.drawString(50, 666, f'Turma: {dados_historico["aluno"]["turma"]}')
    cnv.drawString(50, 649, f'Turno: {dados_historico["aluno"]["turno"]}')
    cnv.drawString(50, 626, f'Disciplinas, notas e faltas:')

    table = Table(dados_historico['historico'])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (2, 0), colors.HexColor(0xdc3545)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ('GRID', (0, 1), (-1, -1), 2, colors.black),
    ])
    table.setStyle(style)

    table.wrapOn(cnv, 400, 200)
    table.drawOn(cnv, 51, 370)

    now = datetime.now().strftime('%d/%m/%Y')

    cnv.drawString(50, 340, f'Emitido em: {now}')

    cnv.drawString(50, 320, f'{"="*70}')
    cnv.drawString(50, 300, f'Coordenador: {dados_historico["coordenador"]["nome"]}')
    cnv.drawString(50, 285, f'Contato: {dados_historico["coordenador"]["contato"]}')
    cnv.drawString(50, 265, f'{"="*70}')
    
    cnv.save()
    buffer.seek(0)

    return buffer
