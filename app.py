from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_mysqldb import MySQL
from datetime import datetime, date
import MySQLdb.cursors

app = Flask(__name__)
app.static_folder = 'static'

app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "impacta123"
app.config["MYSQL_DB"] = "biblioteca"

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/emprestimo', methods=['POST', 'GET'])
def emprestimo():
    if request.method == 'POST':
        _isbn = request.form['inputISBN']
        _titulo = request.form['inputTitulo']
        _autor = request.form['inputAutor']
        _usuario = request.form['inputUsuario']
        
        if _isbn and _titulo and _usuario:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # Verifica se já existe um registro de empréstimo sem devolução para o ISBN fornecido
            cur.execute("SELECT * FROM emprestimos WHERE isbn = %s AND data_devolucao IS NULL", (_isbn,))
            existing_record = cur.fetchone()

            if existing_record:
                error_message = "Este livro já está emprestado."
                cur.close()
                return render_template('index.html', errorEmprestimo=error_message)
            else:
                data_emprestimo = date.today()
                cur.execute("INSERT INTO emprestimos (isbn, titulo, autor, usuario, data_emprestimo) VALUES (%s, %s, %s, %s, %s)",
                            (_isbn, _titulo, _autor, _usuario, data_emprestimo))
                mysql.connection.commit()
                cur.close()

            return redirect(url_for('emprestimo'))
    return render_template('index.html')

@app.route('/devolucao', methods=['POST', 'GET'])
def devolucao():
    if request.method == 'POST':
        if 'inputISBN' in request.form:
            _isbn = request.form['inputISBN']

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT * FROM emprestimos WHERE isbn = %s AND data_devolucao IS NULL", (_isbn,))
            emprestimo = cur.fetchone()

            if emprestimo:
                data_emprestimo = emprestimo['data_emprestimo']
                data_devolucao = datetime.now()

                # Calcular multa por atraso
                multa = calculate_fee(data_emprestimo, data_devolucao)

                # Atualizar registro de empréstimo com a data de devolução
                cur.execute("UPDATE emprestimos SET data_devolucao = %s WHERE isbn = %s AND data_devolucao IS NULL",
                            (data_devolucao, _isbn))
                mysql.connection.commit()
                cur.close()

                return render_template('index.html', message=f"Livro devolvido com sucesso! Multa: R${multa:.2f}")
            else:
                error_message = "Nenhum registro de empréstimo em aberto encontrado para o ISBN fornecido."
                cur.close()
                return render_template('index.html', errorDevolucao=error_message)

    return render_template('index.html')

@app.route('/usuarios', methods=['POST', 'GET'])
def usuarios():
    if request.method == 'POST':
        _nome = request.form['inputNome']
        _email = request.form['inputEmail']

        if _nome and _email:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cur.execute("SELECT * FROM usuarios WHERE email = %s", (_email,))
            existing_record = cur.fetchone()

            if existing_record:
                error_message = "Usuário já cadastrado."
                cur.close()
                return render_template('index.html', errorCadastroUsuario=error_message)
            else:
                cur.execute("INSERT INTO usuarios (nome, email) VALUES (%s, %s)", (_nome, _email))
                mysql.connection.commit()
                cur.close()

                return redirect(url_for('usuarios'))
    return render_template('index.html')

@app.route('/historico_data')
def get_historico_data():
    cur = mysql.connection.cursor()
    query = "SELECT * FROM emprestimos ORDER BY id DESC"
    cur.execute(query)
    result = cur.fetchall()

    data = []
    for row in result:
        data.append({
            'id': row[0],
            'isbn': row[1],
            'titulo': row[2],
            'autor': row[3],
            'usuario': row[4],
            'data_emprestimo': row[5].strftime("%d/%m/%Y"),
            'data_devolucao': str(row[6]) if row[6] else None,
        })

    return jsonify(data)

@app.route('/usuarios_data')
def get_usuarios_data():
    cur = mysql.connection.cursor()
    query = "SELECT * FROM usuarios ORDER BY id DESC"
    cur.execute(query)
    result = cur.fetchall()

    data = []
    for row in result:
        data.append({
            'id': row[0],
            'nome': row[1],
            'email': row[2],
        })
    
    return jsonify(data)

def calculate_fee(data_emprestimo, data_devolucao):
    diff = data_devolucao.date() - data_emprestimo
    dias_atraso = diff.days - 14  # Supondo que o prazo de devolução seja de 14 dias
    
    if dias_atraso > 0:
        fee = dias_atraso * 2  # Exemplo: multa de R$2,00 por dia de atraso
    else:
        fee = 0

    return fee

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)
