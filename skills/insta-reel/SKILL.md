---
name: insta-reel
description: >-
  Escreve o roteiro de um Reel do Instagram em português a partir de uma ideia
  crua: três ganchos com nota (26 fórmulas), a fala, as cartelas de texto na
  tela e o mapa de tempos por sílaba, com legenda .srt pronta para o CapCut.
  Use quando a pessoa pedir um Reel, roteiro de vídeo curto, gancho, narração,
  "faz um reels sobre X", "o que eu falo nesse vídeo" ou estiver para gravar
  sem a primeira frase.
---

# insta-reel

Transforma uma ideia num Reel que a pessoa assiste até o fim.

Os scripts desta pasta rodam de verdade. Use. Não avalie o gancho no olho e
não chute a duração. (No Windows o comando costuma ser `python`; no Mac/Linux,
`python3`.)

```bash
python gancho.py ganchos.txt                      # ranking dos ganchos
python gancho.py --gancho "uma frase"             # nota detalhada de um
python tempos.py roteiro.txt --alvo 30            # mapa de tempos antes de gravar
python tempos.py roteiro.txt --srt-fala fala.srt --srt-tela tela.srt
python tempos.py roteiro.txt --calibrar 27.5      # mede o ritmo da pessoa
python moldura.py                                 # PNG da área segura 9:16
```

## Antes de escrever

1. Leia `~/.claude/instagram/voz.md` se existir. É o perfil de voz da pessoa:
   como fala, o que nunca diz, com quem fala, o ritmo (`--sps`). Se não
   existir, peça **três vídeos ou legendas dela**, deduza a voz e escreva o
   arquivo a partir de `modelos/voz.md`. Roteiro na voz errada não serve,
   porque ela vai ter que falar aquilo em voz alta.
2. Leia `ganchos.json` desta pasta: 26 fórmulas com modelo, exemplo, versão
   de tela, para que serve e como se estraga.
3. Se a ideia está fraca, não encha linguiça. Faça UMA pergunta agrupada: o
   que aconteceu, com quem, quanto custou ou rendeu. Reel precisa de uma coisa
   verdadeira e específica. Consiga antes de escrever.
4. Se a pessoa for gravar a tela de um sistema ou site, pergunte quais telas
   aparecem e em que ordem. O roteiro vai junto com o passo a passo da gravação.

## O formato

Um Reel se decide nos dois primeiros segundos e se mantém nos cinco seguintes.

```
0:00 - 0:02   GANCHO     a promessa. Fala e cartela escritas separadas.
                         Movimento no primeiro quadro, nunca rosto parado.
0:02 - 0:07   O PORQUÊ   por que isso importa para quem assiste. Uma frase.
0:07 - ...    O CORPO    uma ideia por fala, e a imagem muda a cada fala.
ÚLTIMOS 3s    A ENTREGA  cumpre o que o gancho prometeu e faz UM pedido.
ÚLTIMA FALA   O CICLO    repete uma palavra do gancho, para o replay emendar.
```

Duração: de 15 a 45 segundos é a faixa que funciona. Reel vai até 3 minutos
e quase ninguém deve usar. Abaixo de 7 segundos só a contagem de repetição
infla, nada mais.

## O passo a passo

**1. Três ganchos, não um.** Passe a ideia pelas fórmulas de `ganchos.json`,
escolha três que realmente servem e escreva a fala e a cartela de cada uma.
Fórmulas diferentes, não três versões da mesma frase.

**2. Dê nota.** Coloque as três falas num arquivo, uma por linha, e rode
`gancho.py`. Mostre o ranking. Se o primeiro está abaixo de 50, ainda não
existe gancho, e editar não resolve. A nota serve para **descartar o fraco**,
não para garantir o vencedor: diga isso se a pessoa tratar a nota como
previsão.

**3. Escreva a fala** a partir do gancho vencedor. Português falado, do jeito
que a pessoa fala: "pra", "tá", "a gente" se ela fala assim. Frases curtas.
Nada que ela precise ensaiar.

**4. Marque as cartelas.** Na linha de cima da fala em que o texto aparece:

```
[tela: 5 HORAS -> 20 MIN]
Orçamento que levava cinco horas agora sai em vinte minutos.
```

**5. Meça.** `python tempos.py roteiro.txt --alvo {duração} --sps {ritmo}`.
Corrija todo alerta: gancho passando de 3 s, fala com mais de 4 s, sequência
sem nada concreto, sem ciclo, sem cartela no gancho. Rode de novo até limpar.

**6. Humanize.** Releia em voz alta (mentalmente) e corte tudo que soa
escrito: "é importante destacar", "no mundo de hoje", "vale ressaltar",
"diante disso", travessão no meio da frase, três adjetivos seguidos.

**7. Entregue o bloco.** O roteiro num bloco de código, as cartelas como lista
com os tempos e, se pedirem, gere os .srt (`--srt-fala`, `--srt-tela`). Depois:

```
REEL PRONTO
gancho:    #5 Tempo encolhido, nota 86 FORTE
duração:   28,4 s em 9 falas a 5,0 sílabas/s
cartelas:  6
legendas:  fala.srt, tela.srt (CapCut: Texto > Legendas > Importar)
legenda do post: rode /insta-legenda

Responda "ok" para registrar, ou diga o que mudar.
```

**8. Nunca publique.** Esta skill produz roteiro. A pessoa grava e posta. No
"ok", acrescente em `~/.claude/instagram/registro.md` a data, a fórmula do
gancho e a primeira frase.

## Cartela é outro roteiro

Escreva separado, sempre. Ela é lida antes de a fala ser ouvida.

- **Seis palavras ou menos por cartela.** Quem lê está com o celular na mão
  e ainda nem ligou o som.
- **A cartela do gancho está no quadro 1**, não depois de um silêncio.
- **Dentro da área segura.** No quadro 1080x1920, nada acima de y=230 nem
  abaixo de y=1440, e deixe livres os 230 px da direita. Rode `moldura.py`
  e use o PNG como sobreposição no editor enquanto posiciona os textos.
- **Legenda queimada no corpo.** A maioria assiste sem som primeiro.

## Regras que fazem diferença

- **Uma ideia por Reel.** Se o roteiro tem duas, são dois Reels. Diga isso.
- **Número no lugar de adjetivo.** "R$ 4.200" ganha de "muito dinheiro". Se a
  pessoa não deu número, peça em vez de escrever contornando o buraco.
- **Sem introdução.** Sem "oi, pessoal", sem "nesse vídeo", sem nome, sem
  vinheta. O vídeo começa na frase que normalmente viria no sexto segundo.
- **Mude a imagem a cada fala.** Tela parada por 8 segundos é onde a pessoa
  sai, e `tempos.py` aponta isso.
- **Um pedido no final.** Comentar uma palavra, salvar ou seguir. Um.
- **Nunca invente.** Nada de número, cliente, faturamento ou resultado
  inventado no nome da pessoa, nem como exemplo. Se precisa de um número que
  não existe, deixe `{{seu número}}` no roteiro e avise.
- **Dado de cliente nunca aparece.** Em gravação de tela de sistema, use conta
  de demonstração com dados fictícios. Se algo real aparecer, borre.

## Exemplo

```
/insta-reel orçamento que levava 5 horas agora sai em 20 minutos
```

```
GANCHOS (com nota, saída real do gancho.py)
  80  FORTE  #2  Ordem negativa    "Pare de montar orçamento no Word."
                                    tela: PARE DE USAR WORD
  60  OK     #5  Tempo encolhido   "Orçamento levava cinco horas. Agora, vinte minutos."
                                    tela: 5 HORAS -> 20 MIN
  28  FRACO  #18 Demonstração      "Cliente, item, desconto, enviar."
                                    tela: ORÇAMENTO EM 1 MIN

Gravando o #2. O #5 tem o melhor número, mas não fala com ninguém
(PRA QUEM 35): "Seu orçamento leva cinco horas? O meu, vinte minutos."
resolve e vale rodar de novo. O #18 funciona como imagem, não como fala:
use a sequência de cliques na tela, com o #2 narrado por cima.
```
