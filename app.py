from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import random

app = Flask(__name__)
app.secret_key = "ecoquiz_secret_2024"

# Filtro enumerate para Jinja2
app.jinja_env.globals.update(enumerate=enumerate)

# --- MongoDB ---
try:
    client = MongoClient("mongodb+srv://Joao:extensaounip@cluster0.myod2.mongodb.net/quiz_db?retryWrites=true&w=majority")
    db = client.quiz_db
    ranking_collection = db.ranking
    print("✅ MongoDB conectado!")
except Exception as e:
    print(f"❌ Erro MongoDB: {e}")
    client = None

# --- Perguntas de Sustentabilidade (nível 5º ano) ---
PERGUNTAS = [
    {
        "pergunta": "Como a tecnologia pode ajudar a reduzir o uso de papel?",
        "opcoes": ["Imprimindo mais documentos", "Usando arquivos digitais", "Jogando papéis fora", "Escrevendo em folhas maiores"],
        "resposta": "Usando arquivos digitais"
    },
    {
        "pergunta": "Qual dessas ações usa tecnologia para ajudar o meio ambiente?",
        "opcoes": [
            "Deixar o computador ligado o dia todo",
            "Usar aplicativos para controlar o consumo de energia",
            "Imprimir todos os e-mails",
            "Jogar o celular no lixo comum"
        ],
        "resposta": "Usar aplicativos para controlar o consumo de energia"
    },
    {
        "pergunta": "O que fazer com aparelhos eletrônicos antigos?",
        "opcoes": [
            "Jogar no lixo comum",
            "Guardar para sempre",
            "Levar para reciclagem eletrônica",
            "Queimar no quintal"
        ],
        "resposta": "Levar para reciclagem eletrônica"
    },
    {
        "pergunta": "Como a internet pode ajudar na sustentabilidade?",
        "opcoes": [
            "Aumentando o consumo de papel",
            "Facilitando o acesso a informações ambientais",
            "Destruindo florestas",
            "Poluindo rios"
        ],
        "resposta": "Facilitando o acesso a informações ambientais"
    },
    {
        "pergunta": "Qual atitude economiza energia ao usar tecnologia?",
        "opcoes": [
            "Deixar o computador ligado sem uso",
            "Desligar dispositivos quando não estiver usando",
            "Aumentar o brilho ao máximo sempre",
            "Usar vários aparelhos ao mesmo tempo sem necessidade"
        ],
        "resposta": "Desligar dispositivos quando não estiver usando"
    },
    {
        "pergunta": "O que é lixo eletrônico?",
        "opcoes": [
            "Restos de comida",
            "Papéis usados",
            "Equipamentos eletrônicos descartados",
            "Garrafas de plástico"
        ],
        "resposta": "Equipamentos eletrônicos descartados"
    },
    {
        "pergunta": "Como aplicativos podem ajudar no consumo de água?",
        "opcoes": [
            "Aumentando o gasto de água",
            "Controlando e monitorando o uso de água",
            "Desperdiçando água automaticamente",
            "Bloqueando o acesso à água"
        ],
        "resposta": "Controlando e monitorando o uso de água"
    },
    {
        "pergunta": "Qual dessas opções é uma tecnologia sustentável?",
        "opcoes": [
            "Servidores que gastam muita energia",
            "Uso de energia solar em data centers",
            "Queima de carvão para gerar energia",
            "Uso excessivo de papel em escritórios"
        ],
        "resposta": "Uso de energia solar em data centers"
    },
    {
        "pergunta": "Como reduzir o impacto ambiental ao usar celular?",
        "opcoes": [
            "Trocar de celular todo ano",
            "Usar até o fim da vida útil e descartar corretamente",
            "Jogar no lixo comum",
            "Deixar sempre carregando"
        ],
        "resposta": "Usar até o fim da vida útil e descartar corretamente"
    },
    {
        "pergunta": "O que significa usar tecnologia de forma consciente?",
        "opcoes": [
            "Usar sem se preocupar com o consumo",
            "Consumir mais energia sempre",
            "Usar tecnologia evitando desperdícios",
            "Deixar todos os aparelhos ligados"
        ],
        "resposta": "Usar tecnologia evitando desperdícios"
    }
]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/quiz', methods=['POST'])
def quiz():
    nome = request.form.get('nome', '').strip()
    if not nome:
        return redirect(url_for('index'))

    session['nome'] = nome
    perguntas = PERGUNTAS.copy()
    random.shuffle(perguntas)
    session['perguntas'] = perguntas

    return render_template('quiz.html', perguntas=perguntas, nome=nome, total=len(perguntas))


@app.route('/resultado', methods=['POST'])
def resultado():
    nome = session.get('nome', 'Anônimo')
    perguntas = session.get('perguntas', [])

    acertos = 0
    resultados = []

    for i, p in enumerate(perguntas):
        resposta_usuario = request.form.get(f'q{i}', '')
        correta = p['resposta']
        acertou = resposta_usuario.strip() == correta.strip()
        if acertou:
            acertos += 1
        resultados.append({
            'pergunta': p['pergunta'],
            'opcoes': p['opcoes'],
            'resposta_usuario': resposta_usuario,
            'resposta_correta': correta,
            'acertou': acertou
        })

    total = len(perguntas)

    # Salva no MongoDB
    if client:
        try:
            ranking_collection.insert_one({"nome": nome, "acertos": acertos, "total": total})
            print(f"✅ Salvo: {nome} - {acertos}/{total}")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")

    return render_template('resultado.html', nome=nome, acertos=acertos, total=total, resultados=resultados)


@app.route('/ranking')
def ranking():
    top = []
    if client:
        try:
            top = list(ranking_collection.find({}, {'_id': 0}).sort("acertos", -1).limit(10))
        except Exception as e:
            print(f"❌ Erro ao buscar ranking: {e}")
    return render_template('ranking.html', top=top)


if __name__ == '__main__':
    app.run(debug=True)