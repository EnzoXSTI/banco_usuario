def validacao_senha(senha: str):
    t_maiuscula = False
    t_minuscula = False
    t_numero = False
    t_caractere_especial = False
    t_oito = False

    if len(senha) >=8:
        t_oito = True

    for s in senha:
        if s.isupper():
            t_maiuscula = True
        if s.islower():
            t_minuscula = True
        if s.isdigit():
            t_numero = True
        if not s.isalnum():
            t_caractere_especial = True
    if t_maiuscula and t_minuscula and t_numero and t_caractere_especial and t_oito:
        return True