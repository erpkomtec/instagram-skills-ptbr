---
name: insta-legenda
description: >-
  Escreve e confere a legenda (descrição) de um post ou Reel do Instagram em
  português: a primeira linha que sobrevive ao corte do "... mais", o corpo,
  uma única chamada para ação, os termos de busca e até cinco hashtags. Use
  quando pedirem "escreve a legenda", "o que coloco na descrição", tiverem um
  Reel ou carrossel pronto precisando de texto, ou perguntarem de hashtags.
---

# insta-legenda

Um script mora nesta pasta e roda de verdade:

```bash
python legenda.py legenda.txt
python legenda.py legenda.txt --buscas "sistema para oficina,orçamento rápido"
```

Ele mostra a legenda como o feed mostra: os primeiros ~125 caracteres numa
caixa e o resto atrás do toque. Leia essa caixa antes de qualquer outra coisa.

## Primeiro: qual é o trabalho desta legenda

**Trabalho A: o vídeo já prendeu.** O Reel tem o gancho nos dois primeiros
segundos, falado e na tela. A legenda não é um segundo gancho; competir com o
vídeo é perder os dois. O trabalho dela é o pedido, o contexto que faz o
pedido ter sentido e as palavras que as pessoas buscam.

**Trabalho B: a legenda é o conteúdo.** Foto, imagem única, capa de
carrossel. Aqui a primeira linha é o gancho e funciona igual ao do Reel:
concreta, curta, cortada num suspense e não no meio de uma explicação.

Pergunte qual dos dois. Se for Reel com gancho forte, escreva o A e diga por quê.

## O formato

```
Linha 1    ~125 caracteres visíveis. Trabalho A: o pedido, claro.
           Trabalho B: o gancho.
           Nunca cumprimento, nunca hashtag, nunca emoji como 1º caractere.
Corpo      parágrafos curtos, uma linha em branco entre eles. De dois a seis.
           Aqui moram os termos de busca.
O pedido   um só. Comentar uma palavra, salvar, chamar no direct. Um.
Hashtags   até cinco, numa linha no final, ou nenhuma.
```

O limite é 2.200 caracteres e quase nada precisa disso. Legenda que ganha o
toque e entrega 600 caracteres vence a que entrega 1.800.

## Hashtags, com honestidade

Desde 18/12/2025 o Instagram limita **cinco hashtags por post** (antes eram
30). O próprio Instagram vem dizendo que hashtag é rótulo de assunto, não
alavanca de alcance. Então: até cinco, específicas, como rótulo.
`#viral`, `#fyp`, `#explore`, `#sdv`, `#sucesso` não descrevem nada. Corte.

## Termo de busca vale mais que hashtag

A busca do Instagram lê o texto da legenda. A frase pela qual a pessoa quer
ser encontrada entra na legenda como alguém digitaria, numa frase normal:
"sistema para oficina" escrito no texto, não `#sistemaparaoficina` no fim.
Peça dois ou três termos e passe em `--buscas`.

## O passo a passo

1. Descubra o trabalho (A ou B), o pedido único e os termos de busca.
2. Escreva. Leia `~/.claude/instagram/voz.md` antes, se existir.
3. Salve em arquivo e rode `legenda.py` com `--buscas`.
4. Corrija toda FALHA. Para cada AVISO, corrija ou diga por que fica.
5. Entregue a legenda num bloco de código, pronta para copiar, e a caixa do
   que aparece no feed.

## Regras

- **Nunca invente número ou resultado.** Use `{{seu número}}` e avise.
- **Link na legenda não é clicável.** Mande para a bio ou para o direct.
- **Palavra-chave de comentário** ("comente ORÇAMENTO") só se a pessoa tiver
  como responder todo mundo. Prometer e não entregar queima o perfil.
- **Nunca publique.** A pessoa copia e posta.
