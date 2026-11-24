---
name: insta-carrossel
description: >-
  Cria um carrossel de Instagram em português: capa, texto de cada slide,
  legenda e as imagens PNG 1080x1350 prontas para subir. Use quando pedirem
  "carrossel", "slides para o Instagram", "post de arrastar" ou tiverem uma
  ideia em passos, lista ou antes e depois.
---

# insta-carrossel

```bash
python carrossel.py slides.txt                                  # confere
python carrossel.py slides.txt --saida pasta --perfil @perfil   # gera os PNG
```

Aceita `--cor`, `--fundo` e `--texto` em `#RRGGBB`. Usa o Chrome ou Edge
instalado, sem internet.

## Carrossel ou Reel?

Carrossel quando a ideia tem **sequência e precisa ser relida**: passos, lista,
comparação. Reel quando tem movimento ou um resultado para ver acontecendo. Se
é uma frase só, não é nenhum dos dois: passe para `/insta-reel`.

## De trás para frente

Antes da capa, responda: **o que a pessoa consegue fazer depois do último
slide?** Se a resposta for vaga, pare e peça mais material.

```
1        CAPA      até 6 palavras e uma linha de promessa
2        O PORQUÊ  por que importa; funciona sozinho, como segunda capa
3 a N    UMA IDEIA por slide: título de 3 a 7 palavras, até 25 de apoio
N+1      RESUMO    a lista inteira; é o slide que se salva e se envia
ÚLTIMO   O PEDIDO  um só
```

De 6 a 10 slides (o limite é 20). Escreva **cinco capas** com ângulos
diferentes, passe no `gancho.py` da `/insta-reel` para descartar as fracas e
mostre as três melhores.

## O passo a passo

1. Leia `~/.claude/instagram/voz.md`.
2. Escreva o texto numerado e mostre. **Só gere imagem depois do ok.**
3. Passe `/insta-humano` no texto.
4. Salve em `slides.txt` (slides separados por `---`), rode a conferência e
   corrija toda FALHA.
5. Gere os PNG e **abra cada um para ver**: texto cortado, capa legível
   pequena, contraste. Não entregue sem olhar.
6. Escreva a legenda com `/insta-legenda` (trabalho B) e o texto alternativo
   da capa.

## Regras

- Slide de enchimento sai.
- Nada de número, cliente ou depoimento inventado: `{{seu número}}` trava a
  geração de propósito.
- Tela de sistema só com dados de demonstração.
- Nunca publique. A pessoa sobe os arquivos.
