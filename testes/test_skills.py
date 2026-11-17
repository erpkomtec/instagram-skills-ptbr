"""
Testes das skills. Rodar da raiz do repositório:

    python -m unittest discover -s testes -v

Só biblioteca padrão; nada para instalar.
"""

import importlib.util
import json
import os
import re
import struct
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REEL = os.path.join(RAIZ, "skills", "insta-reel")
LEGENDA = os.path.join(RAIZ, "skills", "insta-legenda")


def carregar(pasta, nome):
    """Importa um script de skill como módulo, com a pasta dele no path."""
    sys.path.insert(0, pasta)
    try:
        spec = importlib.util.spec_from_file_location(f"{os.path.basename(pasta)}_{nome}",
                                                      os.path.join(pasta, nome + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path.remove(pasta)


ptbr = carregar(REEL, "ptbr")
tempos = carregar(REEL, "tempos")
gancho = carregar(REEL, "gancho")
moldura = carregar(REEL, "moldura")
legenda = carregar(LEGENDA, "legenda")


class PtbrSincronizado(unittest.TestCase):
    def test_copias_identicas(self):
        """ptbr.py é copiado em cada skill; as cópias não podem divergir."""
        copias = []
        for pasta in sorted(os.listdir(os.path.join(RAIZ, "skills"))):
            arq = os.path.join(RAIZ, "skills", pasta, "ptbr.py")
            if os.path.exists(arq):
                with open(arq, encoding="utf-8") as f:
                    copias.append((pasta, f.read()))
        self.assertGreaterEqual(len(copias), 2)
        for pasta, conteudo in copias[1:]:
            self.assertEqual(conteudo, copias[0][1], f"ptbr.py de {pasta} diverge de {copias[0][0]}")


class Palavras(unittest.TestCase):
    def test_acento_nao_quebra_palavra(self):
        # O bug do original: [A-Za-z] fazia "Não perca orçamento." virar 5 palavras.
        self.assertEqual(ptbr.palavras("Não perca orçamento."), ["Não", "perca", "orçamento"])

    def test_valor_em_reais_e_uma_palavra(self):
        self.assertEqual(ptbr.palavras("custou R$ 1.250,00 ontem"), ["custou", "R$ 1.250,00", "ontem"])

    def test_hifen_e_percentual(self):
        self.assertEqual(ptbr.palavras("bem-vindo a 30% off"), ["bem-vindo", "a", "30%", "off"])

    def test_silabas(self):
        self.assertEqual(ptbr.silabas_palavra("orçamento"), 4)
        self.assertEqual(ptbr.silabas_palavra("não"), 1)
        self.assertEqual(ptbr.silabas("Orçamento que levava cinco horas agora sai em vinte minutos."), 22)

    def test_silabas_de_numero_por_extenso(self):
        casos = {
            "20": 2,            # vinte
            "21": 4,            # vinte e um
            "100": 1,           # cem
            "101": 4,           # cento e um
            "1000": 1,          # mil
            "2026": 7,          # dois mil e vinte e seis
            "1300": 5,          # mil e trezentos
            "R$ 1.250": 10,     # mil duzentos e cinquenta reais
            "R$ 4,50": 11,      # quatro reais e cinquenta centavos
            "30%": 5,           # trinta por cento
        }
        for token, esperado in casos.items():
            self.assertEqual(ptbr.silabas_palavra(token), esperado, token)

    def test_nome_proprio_ignora_inicio_de_frase(self):
        self.assertEqual(ptbr.nomes_proprios("Hoje fui a Goiânia. Depois voltei."), ["Goiânia"])

    def test_raiz_junta_plural(self):
        self.assertEqual(ptbr.raiz("Orçamentos"), ptbr.raiz("orçamento"))


ROTEIRO = """[tela: 5 HORAS -> 20 MIN]
Orçamento que levava cinco horas agora sai em vinte minutos.
Não é mágica, é modelo pronto.
[tela: PDF NO WHATSAPP]
E o PDF vai pro WhatsApp do cliente.
Vinte minutos. Orçamento enviado.
"""


class Tempos(unittest.TestCase):
    def setUp(self):
        self.a = tempos.analisar(ROTEIRO, sps=5.0, alvo=15)

    def test_quatro_falas_e_cartelas(self):
        self.assertEqual(len(self.a["trechos"]), 4)
        self.assertEqual(self.a["trechos"][0]["tela"], ["5 HORAS -> 20 MIN"])
        self.assertEqual(self.a["trechos"][2]["tela"], ["PDF NO WHATSAPP"])

    def test_gancho_longo_alerta(self):
        self.assertTrue(any("passa dos 3s" in x for x in self.a["trechos"][0]["alertas"]))

    def test_ciclo_mostra_palavra_original(self):
        nota = next(n for n in self.a["notas"] if n.startswith("Fecha o ciclo"))
        self.assertIn("orçamento", nota)
        self.assertNotIn("orcamento", nota)

    def test_srt_tela(self):
        srt = tempos.srt_tela(self.a)
        blocos = srt.strip().split("\n\n")
        self.assertEqual(len(blocos), 2)
        self.assertTrue(blocos[0].startswith("1\n00:00:00,000 --> "))
        self.assertIn("5 HORAS -> 20 MIN", blocos[0])

    def test_srt_fala_tempos_crescentes(self):
        srt = tempos.srt_fala(self.a)
        marcas = re.findall(r"(\d\d:\d\d:\d\d,\d{3}) --> (\d\d:\d\d:\d\d,\d{3})", srt)
        self.assertGreaterEqual(len(marcas), 4)
        for ini, fim in marcas:
            self.assertLess(ini, fim)
        for (_, fim), (ini, _) in zip(marcas, marcas[1:]):
            self.assertLessEqual(fim, ini)

    def test_tc_srt(self):
        self.assertEqual(tempos.tc_srt(65.25), "00:01:05,250")

    def test_vazio(self):
        self.assertIsNone(tempos.analisar("\n\n"))


class Gancho(unittest.TestCase):
    def test_cumprimento_e_preambulo_eliminam(self):
        _, nota, veredito, alertas = gancho.avaliar("Oi pessoal, hoje eu vou mostrar como fazer orçamento.")
        self.assertEqual(veredito, "FRACO")
        self.assertEqual(len(alertas), 2)

    def test_ordem_negativa_forte(self):
        _, nota, veredito, _ = gancho.avaliar("Pare de mandar orçamento em Word para o cliente.")
        self.assertEqual(veredito, "FORTE")

    def test_reais_conta_como_concreto_e_tensao(self):
        res, _, _, _ = gancho.avaliar("R$ 4.200 que eu perdi por demorar.")
        self.assertGreaterEqual(res["CONCRETO"][0], 75)
        self.assertEqual(res["TENSÃO"][0], 100.0)

    def test_voce_fala_com_quem_assiste(self):
        res, _, _, _ = gancho.avaliar("Você está perdendo venda por isso.")
        self.assertEqual(res["PRA QUEM"][0], 100.0)


class FormulasDeGancho(unittest.TestCase):
    def test_cada_exemplo_cai_na_propria_formula(self):
        with open(os.path.join(REEL, "ganchos.json"), encoding="utf-8") as f:
            d = json.load(f)
        por_id = {h["id"]: h for h in d["ganchos"]}
        self.assertEqual(sorted(d["ordem_classificacao"]), list(range(1, 27)))

        def classificar(texto):
            for i in d["ordem_classificacao"]:
                if re.search(por_id[i]["reconhece"], texto, re.IGNORECASE):
                    return i
        for h in d["ganchos"]:
            self.assertEqual(classificar(h["exemplo"]), h["id"], h["nome"])


class Legenda(unittest.TestCase):
    def status(self, a, nome):
        return next(c["status"] for c in a["checagens"] if c["checagem"] == nome)

    def test_seis_hashtags_falha(self):
        a = legenda.analisar("Texto com 3 itens.\n\n#a #b #c #d #e #f")
        self.assertEqual(self.status(a, "HASHTAGS"), "FALHA")
        self.assertEqual(a["veredito"], "CORRIGIR")

    def test_hashtag_com_acento(self):
        a = legenda.analisar("Linha 1.\n\n#orçamento #gestão")
        self.assertEqual(a["hashtags"], ["#orçamento", "#gestão"])

    def test_link_com_br(self):
        a = legenda.analisar("Veja em erpkomtec.com.br hoje.")
        self.assertEqual(self.status(a, "LINKS"), "AVISO")

    def test_cumprimento_na_primeira_linha(self):
        a = legenda.analisar("Bom dia, pessoal! Hoje tem novidade.")
        self.assertEqual(self.status(a, "1ª LINHA"), "AVISO")

    def test_uma_chamada(self):
        a = legenda.analisar("Orçamento em 20 minutos. Comente ORÇAMENTO que eu mando.")
        self.assertEqual(a["chamadas"], ["comentar uma palavra"])

    def test_buscas_sem_acento(self):
        a = legenda.analisar("Sistema para oficina em Goiânia.", buscas=["sistema para oficina", "orcamento"])
        self.assertEqual(self.status(a, "BUSCAS"), "AVISO")


class Moldura(unittest.TestCase):
    def test_png_1080x1920(self):
        dados = moldura.gerar()
        self.assertTrue(dados.startswith(b"\x89PNG\r\n\x1a\n"))
        largura, altura = struct.unpack(">II", dados[16:24])
        self.assertEqual((largura, altura), (1080, 1920))


if __name__ == "__main__":
    unittest.main()
