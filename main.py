def calcular_score_confianca(idade_dominio_dias, cnpj_ativo, nota_reclame_aqui):
    score = 0
    
    # Validação do Domínio (Peso: 25%)
    if idade_dominio_dias > 365:
        score += 25
    elif idade_dominio_dias > 90:
        score += 15

    # Validação do CNPJ (Peso: 25%)
    if cnpj_ativo:
        score += 25

    # Validação Reclame Aqui (Peso: 50%)
    if nota_reclame_aqui:
        score += (nota_reclame_aqui / 10) * 50

    return score # Retorna valor de 0 a 100
