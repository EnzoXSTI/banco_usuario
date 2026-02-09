from flask import Flask, jsonify, request
from main import app, con

@app.route('/usuario', methods=['GET'])
def usuario():
    try:
        cur = con.cursor()
        cur.execute("SELECT id_usuario,nome,email,senha FROM ussario ")
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
