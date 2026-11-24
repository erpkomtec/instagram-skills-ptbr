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


# Sílabas de cada número dito por extenso.
_UNID = [0, 1, 1, 1, 2, 2, 1, 2, 2, 2,            # zero..nove ("um", "dois"...)
         1, 2, 2, 2, 3, 2, 3, 4, 3, 4]            # dez..dezenove
_DEZ = [0, 0, 2, 2, 3, 3, 3, 3, 3, 3]             # vinte..noventa
_CEM = [0, 2, 3, 3, 4, 3, 3, 4, 4, 4]             # cento..novecentos


def _sil_ate_999(n):
    if n == 0:
        return 0
    if n == 100:
        return 1                                   # "cem"
    c, resto = divmod(n, 100)
    partes = []
    if c:
        partes.append(_CEM[c])
    if resto:
        if resto < 20:
            partes.append(_UNID[resto])
        else:
            d, u = divmod(resto, 10)
            partes.append(_DEZ[d])
            if u:
                partes.append(_UNID[u])
    return sum(partes) + (len(partes) - 1)        # cada "e" é uma sílaba


def silabas_inteiro(n):
    """Sílabas de um inteiro por extenso: 20 -> "vinte" = 2; 1250 -> "mil duzentos e cinquenta" = 8."""
    if n == 0:
        return 2                                   # "zero"
    total, grupos = 0, []
    while n:
        n, g = divmod(n, 1000)
        grupos.append(g)
    nomes = [0, 1, 2, 2]                           # -, mil, milhões, bilhões
    for i, g in enumerate(grupos):
        if not g:
            continue
        if i == 1 and g == 1:
            total += 1                             # "mil", não "um mil"
        else:
            total += _sil_ate_999(g) + (nomes[i] if i < len(nomes) else 2)
    # "dois mil E vinte", "mil E trezentos"; mas "mil duzentos e cinquenta".
    if len(grupos) > 1 and grupos[0] and (grupos[0] < 100 or grupos[0] % 100 == 0):
        total += 1
    return total


def silabas_palavra(token):
    """Sílabas faladas, por aproximação.

    Palavra: conta grupos de vogais (ditongos contam como um; hiatos como
    "saída" contam a menos, o que dá uma margem de segurança pequena).
    Número: conta como é dito por extenso. R$ 1.250,00 vira "mil duzentos e
    cinquenta reais", 10 sílabas; 20 vira "vinte", 2.
    """
    if eh_numero(token):
        dinheiro = token.startswith("R$")
        corpo = token.replace("R$", "").strip()
        sufixo = re.search(r"[%A-Za-z]+$", corpo)
        sufixo = sufixo.group(0).lower() if sufixo else ""
        corpo = re.sub(r"[%A-Za-z]+$", "", corpo)
        inteiro, _, decimais = corpo.partition(",")
        digitos = re.sub(r"\D", "", inteiro)[:15] or "0"
        total = silabas_inteiro(int(digitos))
        cent = int((re.sub(r"\D", "", decimais) + "00")[:2]) if decimais else 0
        if cent:
            total += 1 + _sil_ate_999(cent) + 3   # "e cinquenta centavos"
        if dinheiro:
            total += 2                      # "reais"
        total += {"%": 3, "h": 2, "min": 3, "x": 2, "k": 1}.get(sufixo, 0)
        return total
    return max(1, len(GRUPO_VOGAL_RE.findall(token)))


def silabas(texto):
    return sum(silabas_palavra(p) for p in palavras(texto))
