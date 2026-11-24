---
name: insta-humano
description: >-
  Tira o jeito de texto de IA de legendas, roteiros e mensagens em português:
  travessões, caracteres invisíveis, expressões batidas e frases de molde. Use
  quando disserem "está com cara de IA", "deixa mais natural", "humaniza", ou
  antes de mostrar qualquer legenda, roteiro, comentário ou direct pronto.
---

# insta-humano

```bash
python humano.py rascunho.txt -o limpo.txt
```

O script corrige sozinho a tipografia (travessão, aspas curvas, caracteres
invisíveis) e **aponta** o resto. Trocar palavra por regex quebra concordância
em português, então reescrever é trabalho seu.

## O passo a passo

1. Rode o script.
2. Reescreva cada linha apontada mantendo o sentido. Não troque um chavão por
   outro: volte ao fato.
3. Rode de novo até sair LIMPO. Mais de três rodadas quer dizer que falta um
   fato no rascunho. Peça o fato.
4. Leia em voz alta, na imaginação. Se a pessoa tropeçaria, está escrito e não
   falado.
5. Confira com `~/instagram-dados/voz.md`. Se a expressão apontada é
   mesmo dela, mantenha e sugira tirar de `vicios.json`.

## Honestidade

- Não é detector de IA e não garante resultado em detector nenhum.
- Serve para o texto soar como a pessoa, **não para esconder o uso de IA**. Se
  a imagem, a voz ou o vídeo foi gerado por IA, o rótulo "Informações de IA"
  do Instagram continua valendo.
- Nunca invente número ou história para o texto parecer concreto.
