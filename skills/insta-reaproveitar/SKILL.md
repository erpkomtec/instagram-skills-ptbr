---
name: insta-reaproveitar
description: >-
  Transforma um conteúdo longo (vídeo, aula, artigo, novidade do sistema,
  apresentação) em vários Reels, carrosséis e Stories que se sustentam
  sozinhos. Use quando disserem "reaproveita isso", "transforma em Reels",
  "corta esse vídeo" ou colarem um texto longo para virar post.
---

# insta-reaproveitar

Leia o material **inteiro** antes de tirar qualquer coisa. Confirme que é da
pessoa ou que ela pode usar.

## Extrair, não resumir

Procure e conte: **afirmações** que dariam discussão, **números**,
**histórias** com cena e custo, **mecanismos** ("funciona assim"), **erros**
admitidos e **frases** prontas.

Menos de quatro achados quer dizer material fraco. Diga isso em vez de
espremer.

## Formato de cada um

- Afirmação, erro, história: Reel.
- Mecanismo, lista: carrossel.
- Frase: Story.

Cada peça se sustenta sozinha. Nunca "como eu disse no vídeo". Varie a fórmula
de gancho (`ganchos.json` da `/insta-reel`). Se o original é vídeo da pessoa,
use o trecho real, cortando na frase.

## Saída

A contagem dos achados e a lista de peças: formato, ângulo, gancho e de onde
saiu (minuto ou parágrafo). A mais forte primeiro.

Escreva **uma por vez**, a pedido, por `/insta-reel` ou `/insta-carrossel`, e
passe `/insta-humano`. Dado de cliente no material original não vai para o
post.
