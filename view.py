from flask import Flask, jsonify, request, send_file
from main import app, con
from funcao import validacao_senha
from flask_bcrypt import generate_password_hash, check_password_hash
from fpdf import FPDF


@app.route('/livro', methods=['GET'])
def livro():
    try:
        cur = con.cursor()
        cur.execute("SELECT id_livro, titulo, autor,ano_publicacao FROM livro ")
        livros = cur.fetchall()
        livros_list = []
        for livro in livros:
            livros_list.append({
                'id_livro': livro[0]
                , 'titulo': livro[1]
                , 'autor': livro[2]
                , 'ano_publicacao': livro[3]
            })
        return jsonify(mensagem='lista de livros', livros=livros_list)
    except Exception as e:
        return jsonify(mensagem=f"Erro ao consultar banco de dados: {e}"), 500
    finally:
        cur.close()


@app.route('/criar_livro', methods=['POST'])
def criar_livro():
    dados = request.get_json()

    titulo = dados.get('titulo')
    autor = dados.get('autor')
    ano_publicacao = dados.get('ano_publicacao')
    try:
        cur = con.cursor()
        cur.execute("select 1 from livro where titulo = ?", (titulo,))
        if cur.fetchone():
            return jsonify({"erro": "livro ja existe"}), 400
        cur.execute("""INSERT INTO livro (titulo, autor, ano_publicacao) values (?, ?, ?)""",
                    (titulo, autor, ano_publicacao))
        con.commit()
        return jsonify({
            'mensagem': "Livro cadastrado com sucesso!",
            'livro': {
                'titulo': titulo,
                'autor': autor,
                'ano_publicacao': ano_publicacao
            }
        }), 201
    except Exception as e:
        return jsonify(mensagem=f"Erro ao cadastrar livro: {e}"), 500
    finally:
        cur.close()

@app.route('/editar_livros/<int:id>', methods= ['PUT'])
def editar_livros(id):

    try:
        cur = con.cursor()
        cur.execute("""select id_livro, titulo, autor, ano_publicacao 
                    from livro
                    where id_livro = ? """, (id, ))
        tem_livro = cur.fetchone()
        if not tem_livro:
            cur.close()
            return jsonify({"error": "livro nao encontrado"}), 404
        data = request.get_json()
        titulo = data.get('titulo')
        autor = data.get('autor')
        ano_publicacao = data.get('ano_publicacao')

        cur.execute("""update livro set titulo =?, autor =?, ano_publicacao =?
                        where id_livro = ? """, (titulo, autor, ano_publicacao, id))
        con.commit()
        cur.close()
    finally:

        return jsonify({"message": "Livro atualizado com sucesso",
                        'livro':
                            {
                             'id_livro': id,
                             'titulo': titulo,
                             'autor': autor,
                             'ano_publicacao': ano_publicacao
                             }
                        })

@app.route('/delete_livro/<id>', methods=['DELETE'])
def delete_livro(id):
    cur = con.cursor()
    cur.execute("select 1 from livro where id_livro = ?", (id,))
    if not cur.fetchone():
        cur.close()
        return jsonify({"error": "Livro nao encontrado"}), 404
    cur.execute("delete from livro where id_livro = ?", (id ,))
    con.commit()
    cur.close()

    return jsonify({"message": "Livro execluido com sucesso", 'id_livro': id}), 200


@app.route('/usuario', methods=['GET'])
def usuario():
    try:
        cur = con.cursor()
        cur.execute("SELECT id_usuario,nome,email,senha FROM usuarios ")
        usuarios = cur.fetchall()
        usuarios_list = []
        for usuario in usuarios:
            usuarios_list.append({
                'id_usario': usuario[0]
                , 'nome': usuario[1]
                , 'email': usuario[2]
                , 'senha': usuario[3]
            })
        return jsonify(mensagem='lista de usuario', usuarios=usuarios_list)
    except Exception as e:
        return jsonify(mensagem=f"Erro ao consultar banco de dados: {e}"), 500
    finally:
        cur.close()


@app.route('/criar_usuario', methods=['POST'])
def criar_usuario():
    dados = request.get_json()

    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    try:
        cur = con.cursor()
        cur.execute("select 1 from usuarios where nome = ?", (nome,))
        if cur.fetchone():
            return jsonify({"erro": "Usuario ja existe"}), 400
        if not validacao_senha(senha):
            return jsonify({"error": "Senha deve ter pelo 8 caracteres,incluindo letras maiúsculas, minúsculas, numeros ecaracteres especiais."}), 400

        senha_hash = generate_password_hash(senha).decode('utf-8')

        cur.execute("""INSERT INTO usuarios (nome, email, senha ) values (?, ?, ?)""",
                    (nome, email, senha_hash))
        con.commit()
        return jsonify({
            'mensagem': "usuario cadastrado com sucesso!",
            'usuario': {
                'nome': nome,
                'email': email,
                'senha': senha
            }
        }), 201
    except Exception as e:
        return jsonify(mensagem=f"Erro ao cadastrar Usuario: {e}"), 500
    finally:
        cur.close()

@app.route('/editar_usuario/<int:id>', methods= ['PUT'])
def editar_usuario(id):

    try:
        cur = con.cursor()
        cur.execute("""select id_usuario, nome, email, senha 
                    from usuarios
                    where id_usuario = ? """, (id, ))
        tem_usuario = cur.fetchone()
        if not tem_usuario:
            cur.close()
            return jsonify({"error": "Usuario não encontrado"}), 404
        data = request.get_json()
        nome = data.get('nome')
        email = data.get('email')
        senha = data.get('senha')

        cur.execute("""update usuarios set nome =?, email =?, senha =?
                        where id_usuario = ? """, (nome, email, senha, id))
        con.commit()
        cur.close()
    finally:

        return jsonify({"message": "Usuario atualizado com sucesso",
                        'usuario':
                            {
                             'id_usuario': id,
                             'nome': nome,
                             'email': email,
                             'senha': senha
                             }
                        })

@app.route('/delete_usuario/<id>', methods=['DELETE'])
def delete_usuario(id):
    cur = con.cursor()
    cur.execute("select 1 from usuarios where id_usuario = ?", (id,))
    if not cur.fetchone():
        cur.close()
        return jsonify({"error": "Usuario não encontrado"}), 404
    cur.execute("delete from usuarios where id_usuario = ?", (id,))
    con.commit()
    cur.close()

    return jsonify({"message": "Usuario execluido com sucesso", 'id_usuario': id}), 200

@app.route('/login', methods = ['GET'])
def login():
    dados = request.get_json()

    email = dados.get('email')
    senha = dados.get('senha')

    if not email or not senha:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    try:
        cur = con.cursor()
        cur.execute(
            "SELECT id_usuario, nome, email, senha FROM usuarios WHERE email = ?",
            (email,)
        )
        usuario = cur.fetchone()

        if not usuario:
            return jsonify({"error": "Email ou senha inválidos"}), 401

        senha_hash = usuario[3]

        if not check_password_hash(senha_hash, senha):
            return jsonify({"error": "Email ou senha inválidos"}), 401

        return jsonify({
            "message": "Login realizado com sucesso",
            "usuario": {
                "id_usuario": usuario[0],
                "nome": usuario[1],
                "email": usuario[2]
            }
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao realizar login: {e}"}), 500
    finally:
        cur.close()

@app.route('/livros_relatorio', methods=['GET'])
def livros_relatorio():
    cursor = con.cursor()
    cursor.execute("SELECT id_livro, titulo, autor, ano_publicacao FROM livros")
    livros = cursor.fetchall()
    cursor.close()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Relatorio de Livros", ln=True, align='C')
    pdf.ln(5)  # Espaço entre o título e a linha
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Linha abaixo do título
    pdf.ln(5)  # Espaço após a linha

    pdf.set_font("Arial", size=12)
    for livro in livros:
        pdf.cell(200, 10, f"ID: {livro[0]} - {livro[1]} - {livro[2]} - {livro[3]}", ln=True)

    contador_livros = len(livros)
    pdf.ln(10)  # Espaço antes do contador
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, f"Total de livros cadastrados: {contador_livros}", ln=True, align='C')

    pdf_path = "relatorio_livros.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True, mimetype='application/pdf')