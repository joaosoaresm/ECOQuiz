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
        "pergunta": "O que devemos fazer com garrafas plásticas para ajudar o meio ambiente?",
        "opcoes": ["Jogar no rio", "Reciclar ou reutilizar", "Queimar no quintal", "Enterrar na terra"],
        "resposta": "Reciclar ou reutilizar"
    },
    {
        "pergunta": "Por que é importante economizar água em casa?",
        "opcoes": [
            "Porque a água é infinita",
            "Para pagar menos na conta",
            "Porque a água limpa é um recurso limitado e precioso",
            "Para deixar mais água para os peixes"
        ],
        "resposta": "Porque a água limpa é um recurso limitado e precioso"
    },
    {
        "pergunta": "O que é reciclagem?",
        "opcoes": [
            "Jogar o lixo em qualquer lugar",
            "Transformar materiais usados em novos produtos",
            "Esconder o lixo embaixo da terra",
            "Vender objetos velhos"
        ],
        "resposta": "Transformar materiais usados em novos produtos"
    },
    {
        "pergunta": "Qual dessas atitudes ajuda a economizar energia elétrica?",
        "opcoes": [
            "Deixar as luzes acesas em todos os cômodos",
            "Usar o ar-condicionado com a janela aberta",
            "Apagar as luzes ao sair de um cômodo",
            "Deixar o televisor ligado sem assistir"
        ],
        "resposta": "Apagar as luzes ao sair de um cômodo"
    },
    {
        "pergunta": "O que acontece quando as florestas são desmatadas?",
        "opcoes": [
            "Surgem mais animais silvestres",
            "O ar fica mais limpo",
            "Muitos animais perdem seu habitat e podem desaparecer",
            "Chove mais na região"
        ],
        "resposta": "Muitos animais perdem seu habitat e podem desaparecer"
    },
    {
        "pergunta": "Para que serve a coleta seletiva de lixo?",
        "opcoes": [
            "Para deixar as ruas mais coloridas",
            "Para separar os materiais e facilitar a reciclagem",
            "Para juntar todo o lixo em um único lugar",
            "Para queimar o lixo com mais facilidade"
        ],
        "resposta": "Para separar os materiais e facilitar a reciclagem"
    },
    {
        "pergunta": "O que é energia solar?",
        "opcoes": [
            "Energia gerada pela queima de carvão",
            "Energia que vem da força do vento",
            "Energia gerada aproveitando a luz do Sol",
            "Energia produzida pela água dos rios"
        ],
        "resposta": "Energia gerada aproveitando a luz do Sol"
    },
    {
        "pergunta": "Por que devemos evitar o uso excessivo de sacolas plásticas?",
        "opcoes": [
            "Porque são muito caras",
            "Porque demoram centenas de anos para se decompor na natureza",
            "Porque são muito pesadas",
            "Porque deixam as compras mais difíceis"
        ],
        "resposta": "Porque demoram centenas de anos para se decompor na natureza"
    },
    {
        "pergunta": "O que significa 'reduzir, reutilizar e reciclar'?",
        "opcoes": [
            "Comprar mais coisas novas sempre que possível",
            "Jogar fora tudo que não usa mais",
            "Consumir menos, aproveitar os objetos e reciclar o lixo",
            "Guardar todo o lixo dentro de casa"
        ],
        "resposta": "Consumir menos, aproveitar os objetos e reciclar o lixo"
    },
    {
        "pergunta": "Qual das opções é um exemplo de energia renovável?",
        "opcoes": [
            "Petróleo",
            "Carvão mineral",
            "Gás natural",
            "Energia eólica (vento)"
        ],
        "resposta": "Energia eólica (vento)"
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