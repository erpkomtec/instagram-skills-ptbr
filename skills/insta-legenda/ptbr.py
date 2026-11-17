"""
ptbr.py - o que os scripts precisam saber sobre português falado.

Este arquivo é idêntico em todas as pastas de skill que o usam (cada skill tem
que funcionar sozinha quando copiada para ~/.claude/skills). O teste
testes/test_ptbr_sincronizado.py falha se as cópias divergirem.

Nada aqui acessa a internet nem lê arquivos: só texto entrando e saindo.
"""

import re
import unicodedata

# Uma "palavra" é o que se fala de uma vez:
#   R$ 1.250,00   -> uma palavra (dita "mil duzentos e cinquenta reais")
#   30%  2h  3x   -> uma palavra
#   não, orçamento, bem-vindo, d'água -> uma palavra cada
TOKEN_RE = re.compile(
    r"R\$\s?\d[\d.,]*"
    r"|\d[\d.,]*(?:%|[A-Za-z]{1,3}\b)?"
    r"|[^\W\d_]+(?:[-'’][^\W\d_]+)*"
)

DINHEIRO_RE = re.compile(r"R\$\s?\d")
NUMERO_RE = re.compile(r"^(?:R\$\s?)?\d")

VOGAIS = "aeiouáéíóúâêôãõàüyAEIOUÁÉÍÓÚÂÊÔÃÕÀÜY"
GRUPO_VOGAL_RE = re.compile(f"[{VOGAIS}]+")

# Palavras que não carregam assunto: ficam fora da comparação gancho x final.
STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "da", "do", "das",
    "dos", "e", "ou", "mas", "se", "que", "em", "no", "na", "nos", "nas", "por",
    "pra", "para", "pro", "com", "sem", "ao", "aos", "à", "às", "é", "foi", "era",
    "ser", "são", "está", "tá", "eu", "você", "vocês", "ele", "ela", "eles",
    "elas", "nós", "a gente", "me", "te", "se", "lhe", "meu", "minha", "seu",
    "sua", "isso", "isto", "esse", "essa", "este", "esta", "aquele", "aquela",
    "não", "sim", "já", "só", "mais", "menos", "muito", "bem", "tem", "ter",
    "vai", "vou", "faz", "fazer", "como", "quando", "onde", "aqui", "lá", "então",
    "também", "até", "né", "aí",
}

NUMEROS_FALADOS = {
    "dois", "duas", "três", "quatro", "cinco", "seis", "sete", "oito", "nove",
    "dez", "onze", "doze", "treze", "quinze", "vinte", "trinta", "quarenta",
    "cinquenta", "sessenta", "setenta", "oitenta", "noventa", "cem", "cento",
    "duzentos", "trezentos", "quinhentos", "mil", "milhão", "milhões", "bilhão",
    "bilhões", "dúzia", "dezena", "metade", "dobro", "triplo", "meia",
}
# "um/uma" e "primeiro" ficam de fora de propósito: são enchimento muito mais
# vezes do que são quantidade.

PALAVRAS_DINHEIRO = {
    "reais", "real", "centavos", "conto", "contos", "pila", "porcento",
    "faturamento", "lucro", "prejuízo", "salário", "aluguel", "imposto",
    "impostos", "multa", "multas", "juros", "boleto", "boletos", "caixa",
    "margem", "custo", "custos", "preço",
}


def sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto)
                   if unicodedata.category(c) != "Mn")


def palavras(texto):
    """Lista de palavras faladas, na ordem."""
    return [t.strip() for t in TOKEN_RE.findall(texto)]


def minusculas(texto):
    return [p.lower() for p in palavras(texto)]


def eh_numero(token):
    return bool(NUMERO_RE.match(token))


def raiz(token):
    """Comparação frouxa: sem acento, minúscula, sem plural simples."""
    t = sem_acento(token.lower())
    for fim in ("oes", "aes", "ns", "s"):
        if len(t) > 4 and t.endswith(fim):
            return t[: -len(fim)] + ("ao" if fim in ("oes", "aes") else "m" if fim == "ns" else "")
    return t


def nomes_proprios(texto):
    """Palavras com inicial maiúscula que não estão abrindo frase."""
    achados = []
    inicio_de_frase = True
    for m in re.finditer(r"[.!?]+|" + TOKEN_RE.pattern, texto):
        tok = m.group(0)
        if re.fullmatch(r"[.!?]+", tok):
            inicio_de_frase = True
            continue
        if (not inicio_de_frase and len(tok) >= 3 and tok[0].isupper()
                and not eh_numero(tok) and not tok.isupper()):
            achados.append(tok)
        inicio_de_frase = False
    return achados


def silabas_palavra(token):
    """Sílabas faladas, por aproximação.

    Palavra: conta grupos de vogais (ditongos contam como um; hiatos como
    "saída" contam a menos, o que dá uma margem de segurança pequena).
    Número: estima como é dito por extenso. R$ 1.250,00 vira "mil duzentos e
    cinquenta reais", uns 11.
    """
    if eh_numero(token):
        dinheiro = token.startswith("R$")
        corpo = token.replace("R$", "").strip()
        sufixo = re.search(r"[%A-Za-z]+$", corpo)
        sufixo = sufixo.group(0).lower() if sufixo else ""
        corpo = re.sub(r"[%A-Za-z]+$", "", corpo)
        inteiro, _, decimais = corpo.partition(",")
        digitos = re.sub(r"\D", "", inteiro)
        significativos = sum(1 for d in digitos if d != "0") or 1
        total = significativos * 3
        if len(digitos) >= 4:
            total += 1                      # "mil"
        if len(digitos) >= 7:
            total += 2                      # "milhões"
        if decimais and set(decimais) - {"0"}:
            total += 4                      # "e cinquenta centavos"
        if dinheiro:
            total += 2                      # "reais"
        total += {"%": 3, "h": 2, "min": 3, "x": 2, "k": 1}.get(sufixo, 0)
        return total
    return max(1, len(GRUPO_VOGAL_RE.findall(token)))


def silabas(texto):
    return sum(silabas_palavra(p) for p in palavras(texto))
