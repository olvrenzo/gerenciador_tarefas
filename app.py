import sqlite3
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para usar mensagens flash


# Função para conectar ao banco de dados SQLite
def get_db_connection():
  conn = sqlite3.connect('database.db')
  conn.row_factory = sqlite3.Row  # Permite acessar as colunas pelo nome
  return conn


# Função para inicializar o banco de dados e criar a tabela se não existir
def init_sqlite_db():
  conn = get_db_connection()
  conn.execute(
      'CREATE TABLE IF NOT EXISTS tarefas ('
      'id INTEGER PRIMARY KEY AUTOINCREMENT, '
      'titulo TEXT NOT NULL, '
      'descricao TEXT, '
      'status TEXT NOT NULL DEFAULT "pendente")'
  )
  conn.commit()
  conn.close()


# Rota Principal: Listar tarefas e formulário de cadastro
@app.route('/')
def index():
  conn = get_db_connection()
  tarefas = conn.execute('SELECT * FROM tarefas').fetchall()
  conn.close()
  return render_template('index.html', tarefas=tarefas)


# Rota para Cadastrar uma Nova Tarefa
@app.route('/adicionar', methods=['POST'])
def adicionar():
  titulo = request.form['titulo']
  descricao = request.form['descricao']

  if not titulo:
    flash('O título da tarefa é obrigatório!', 'danger')
  else:
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO tarefas (titulo, descricao, status) VALUES (?, ?, ?)',
        (titulo, descricao, 'pendente'),
    )
    conn.commit()
    conn.close()
    flash('Tarefa cadastrada com sucesso!', 'success')

  return redirect(url_for('index'))


# Rota para Alternar o Status (Pendente <-> Concluída)
@app.route('/mudar_status/<int:id>', methods=['POST'])
def mudar_status(id):
  conn = get_db_connection()
  tarefa = conn.execute(
      'SELECT * FROM tarefas WHERE id = ?', (id,)
  ).fetchone()

  if tarefa:
    novo_status = (
        'concluida' if tarefa['status'] == 'pendente' else 'pendente'
    )
    conn.execute(
        'UPDATE tarefas SET status = ? WHERE id = ?', (novo_status, id)
    )
    conn.commit()
    flash('Status da tarefa atualizado!', 'info')

  conn.close()
  return redirect(url_for('index'))


# Rota para Excluir uma Tarefa
@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
  conn = get_db_connection()
  conn.execute('DELETE FROM tarefas WHERE id = ?', (id,))
  conn.commit()
  conn.close()
  flash('Tarefa excluída com sucesso!', 'warning')
  return redirect(url_for('index'))


if __name__ == '__main__':
  init_sqlite_db()
  app.run(debug=True)