"""Testes das skills da v0.2 (auditoria, pesquisa, humano, carrossel) e dos SKILL.md."""

import contextlib
import io
import os
import re
import unittest

from test_skills import RAIZ, carregar

PASTA = os.path.join(RAIZ, "skills")
auditoria = carregar(os.path.join(PASTA, "insta-auditoria"), "auditoria")
pesquisa = carregar(os.path.join(PASTA, "insta-pesquisa"), "pesquisa")
humano = carregar(os.path.join(PASTA, "insta-humano"), "humano")
carrossel = carregar(os.path.join(PASTA, "insta-carrossel"), "carrossel")


def tsv(*linhas):
    return "\n".join("\t".join(l) for l in linhas) + "\n"


CAB = ("post", "horas", "visualizacoes", "alcance", "nao_seguidores", "retencao_3s", "compartilhamentos")


def auditar(*posts):
    return auditoria.analisar(auditoria.ler(tsv(CAB, *posts)))


class Auditoria(unittest.TestCase):
    def test_numero_brasileiro(self):
        casos = (("1.234", 1234), ("12,5%", 12.5), ("1,2 mil", 1200), ("", None),
                 ("-", None), ("28", 28), ("nan", None))
        for txt, esperado in casos:
            self.assertEqual(auditoria.numero(txt), esperado, txt)

    def test_post_recente_fora_da_mediana(self):
        a = auditar(("A", "72", "20"), ("B", "72", "30"), ("C", "1", "500"))
        self.assertEqual(a["mediana"], 25)
        self.assertEqual([p["post"] for p in a["recentes"]], ["C"])

    def test_vazio_nao_vira_zero(self):
        a = auditar(("A", "72", "20", "100"))
        self.assertIsNone(a["posts"][0]["envios_por_alcance"])
        self.assertIn("NÃO DÁ PARA DIZER", a["gargalo"])

    def test_gargalo_gancho_e_alcance(self):
        self.assertIn("GANCHO", auditar(("A", "72", "20", "100", "7,4%", "30%", "1"))["gargalo"][:6])
        self.assertIn("ALCANCE", auditar(("A", "72", "20", "100", "7,4%", "", "1"))["gargalo"])

    def test_amostra_pequena_confianca_baixa(self):
        self.assertEqual(auditoria.confianca(9)[0], "BAIXA")

    def test_dois_posts_nao_viram_comparacao(self):
        a = auditar(("A", "72", "20", "", "5", "40"), ("B", "72", "30", "", "9", "60"))
        self.assertEqual(a["topo_x_fundo"], {})

    def test_leitura_repetida_conta_um_post(self):
        a = auditar(("A", "72", "20"), ("B", "72", "30"), ("a", "90", "40"))
        self.assertEqual(a["n"], 2)
        self.assertEqual(a["mediana"], 35)

    def test_tudo_recente_nao_quebra(self):
        a = auditar(("A", "1", "20"))
        self.assertIsNone(a["mediana"])
        with contextlib.redirect_stdout(io.StringIO()):
            auditoria.mostrar(a)


class Pesquisa(unittest.TestCase):
    def test_ordena_por_multiplo_e_separa_base_fraca(self):
        t = tsv(("conta", "seguidores", "mediana", "visualizacoes", "gancho"),
                ("@g", "2000000", "400000", "400 mil", "Dica de hoje"),
                ("@p", "4000", "1000", "40.000", "Pare de usar caderno na oficina"),
                ("@s", "10", "", "9000", "Outro gancho"))
        a = pesquisa.analisar(pesquisa.ler(t))
        self.assertEqual([r["conta"] for r in a["reels"]], ["@p", "@g", "@s"])
        self.assertEqual(a["reels"][0]["multiplo"], 40)
        self.assertIn("base fraca", pesquisa.texto(a))

    def test_usa_formulas_e_nota_do_reel(self):
        a = pesquisa.analisar([{"conta": "@a", "seguidores": 1, "mediana": 1, "visualizacoes": 1,
                                "gancho": "Pare de montar orçamento no Word."}])
        self.assertIsNotNone(a["reels"][0]["formula_id"])
        self.assertIsNotNone(a["reels"][0]["nota"])


class Humano(unittest.TestCase):
    def test_travessao_aspas_e_invisivel(self):
        t, m = humano.limpar("Orçamento — rápido​, “pronto”…")
        self.assertEqual(t, 'Orçamento, rápido, "pronto"...')
        self.assertEqual(m["caractere invisível"], 1)

    def test_emoji_composto_fica_inteiro(self):
        emoji = "\U0001F469‍\U0001F527"
        self.assertIn(emoji, humano.limpar(f"A técnica {emoji} chegou")[0])

    def test_url_intacta(self):
        self.assertEqual(humano.limpar("https://x.com/a—b")[0], "https://x.com/a—b")

    def test_texto_normal_nao_muda(self):
        t = "Preço: R$ 1.250,00, à vista.\n- bem-vindo\n"
        self.assertEqual(humano.limpar(t), (t, {}))

    def test_aponta_vicio(self):
        a = humano.avaliar("Vale ressaltar que a solução completa vai alavancar sua oficina.")
        self.assertEqual(a["veredito"], "REESCREVER")

    def test_texto_de_gente_passa(self):
        a = humano.avaliar("Cliente pediu preço às 18h. Mandei o PDF às 18h04. "
                           "Ele fechou R$ 3.200 na hora, pelo WhatsApp.")
        self.assertEqual(a["veredito"], "LIMPO", a["apontar"])

    def test_lista_de_emoji(self):
        a = humano.avaliar("✅ um\n✅ dois\n✅ três\n")
        self.assertTrue(any("emoji" in d for _, d in a["apontar"]))

    def test_vicios_compilam(self):
        v = humano.vicios()
        for e in v["expressoes"] + v["formas"]:
            re.compile(e["busca"])


class Carrossel(unittest.TestCase):
    def niveis(self, *slides):
        return [n for n, _ in carrossel.conferir(carrossel.ler("\n---\n".join(slides)))]

    def test_slides_bons_passam(self):
        self.assertEqual(self.niveis("CAPA", "B", "C", "D", "E", "F"), [])

    def test_slide_longo_falha(self):
        self.assertIn("FALHA", self.niveis("CAPA", "Dois\n" + "palavra " * 30, "C", "D", "E", "F"))

    def test_campo_por_preencher_falha(self):
        self.assertIn("FALHA", self.niveis("CAPA {{seu número}}", "B", "C", "D", "E", "F"))

    def test_html_escapado(self):
        h = carrossel.pagina({"titulo": "<b>", "apoio": "a & b"}, 1, 1, "@x", "#FF7A00", "#000000", "#FFFFFF")
        self.assertIn("&lt;b&gt;", h)


class Skills(unittest.TestCase):
    def ler(self, pasta):
        with open(os.path.join(PASTA, pasta, "SKILL.md"), encoding="utf-8") as f:
            return f.read()

    def test_cada_skill_tem_cabecalho_certo(self):
        for pasta in sorted(os.listdir(PASTA)):
            self.assertTrue(self.ler(pasta).startswith(f"---\nname: {pasta}\ndescription: >-\n"), pasta)

    def test_comando_citado_existe(self):
        nomes = set(os.listdir(PASTA))
        for pasta in nomes:
            for c in re.findall(r"`/(insta-[a-z]+)", self.ler(pasta)):
                self.assertIn(c, nomes, f"{pasta} cita /{c}")


if __name__ == "__main__":
    unittest.main()
