import uuid
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def gerar_atestado_de_matricula(dados_atestado):
    cnv = canvas.Canvas('atestado_de_matricula.pdf', pagesize=A4)

    cnv.drawString(50, 800, f'{"="*70}')
    cnv.drawString(220, 775, f'ATESTADO DE MATRÍCULA')
    cnv.drawString(50, 750, f'{"="*70}')

    cnv.drawString(50, 700, f'Eu, {dados_atestado["coordenador"]["nome"]}, Coordenador(a) da {dados_atestado["instituicao"]["nome"]},')
    cnv.drawString(50, 683, f'localizada na {dados_atestado["instituicao"]["endereco"]}, atesto que:')

    cnv.drawString(50, 650, f'Nome do Aluno(a): {dados_atestado["aluno"]["nome"]}')
    cnv.drawString(50, 633, f'Matrícula: {dados_atestado["aluno"]["matricula"]}')
    cnv.drawString(50, 616, f'Turma: {dados_atestado["aluno"]["turma"]}')
    cnv.drawString(50, 599, f'Período Letivo: {dados_atestado["aluno"]["periodo"]}')
    
    
    cnv.drawString(50, 566, 'Encontra-se regularmente matriculado(a) nesta instituição, frequentando')
    cnv.drawString(50, 549, 'assiduamente as aulas.')

    now = datetime.now().strftime('%d/%m/%Y')

    cnv.drawString(50, 516, f'Emitido em: {now}')

    cnv.drawString(50, 466, f'{"="*70}')
    cnv.drawString(50, 449, f'{dados_atestado["coordenador"]["nome"]}')
    cnv.drawString(50, 432, f'{dados_atestado["coordenador"]["contato"]}')
    cnv.drawString(50, 415, f'{"="*70}')

    cnv.save()


dados_atestado = {
    'coordenador': {
        'nome': 'Luciano',
        'contato': '40028922'
    },
    'instituicao': {
        'nome': 'ivo silveira',
        'endereco': 'rua dos anjos 12'
    },
    'aluno': {
        'nome': 'Diego',
        'matricula': uuid.uuid4(),
        'turma': '1 ano',
        'periodo': '2'
    }
}


gerar_atestado_de_matricula(dados_atestado)
