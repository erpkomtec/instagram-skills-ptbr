---
name: insta-plano
description: >-
  Monta a semana do Instagram dentro do tempo que a pessoa tem: o que postar,
  em que formato, quando, com que material e com quem interagir. Use quando
  pedirem "planeja minha semana", "calendário de conteúdo", "cronograma de
  posts" ou "o que eu posto essa semana".
---

# insta-plano

As outras skills executam. Esta decide o que vale executar.

## Antes

Leia em `~/.claude/instagram/`, se existirem: `voz.md`, `metricas.tsv`,
`testes.md`, `pautas.md`, `referencias.md` e `registro.md`. A evidência da
conta vale mais do que qualquer regra daqui. Pergunte numa mensagem só o que
faltar:

1. **Quantas horas** há para isso na semana, e em que dias?
2. O que já está gravado ou pronto?
3. O que aconteceu na semana (dúvida de cliente, erro, entrega, número)?

## Orçamento de tempo primeiro

Estime cada peça com o histórico da pessoa e some. **Se passar das horas
disponíveis, corte posts**, não sono. Dois bons e publicados valem mais do
que cinco planejados.

## A mistura

| Tipo | Frequência | Trabalho |
|---|---|---|
| Prova | 1 por semana | algo que aconteceu, com número |
| Ensino | 1 ou 2 por semana | uma coisa para fazer hoje |
| Opinião | até 1 por semana | posição da pessoa, sem política partidária |
| História | 1 a cada 15 dias | uma cena com um custo |
| Oferta | 1 a cada 15 dias | o que vende, dito claro |

Ao menos metade em Reel quando o objetivo é chegar a quem não segue. Dê um
**ângulo**, não um tema. Nunca dois iguais seguidos, e não repita tema dos
últimos 15 dias.

**Horário é hipótese de teste**, sem "melhor horário". Os dois primeiros
segundos pesam mais.

## Cada item

Dia e hora de teste · formato · tipo · ângulo · gancho (fórmula) · pedido
único · material necessário · métrica principal · tempo estimado.

Veja também o que se **reaproveita** sem repetir a mensagem (`/insta-reaproveitar`)
e separe o trabalho em blocos: escrever, gravar, montar, revisar, agendar.

Inclua a rodada de interação: até 20 minutos por dia, dez contas aprovadas
pela pessoa (5 de alcance, 3 do mesmo tamanho, 2 que poderiam comprar). Os
textos saem de `/insta-comentario`.

## Saída

Calendário de sete dias, soma das horas contra o disponível e checklist
diário. Salve em `~/.claude/instagram/plano.md`. **Nada é agendado nem
publicado por aqui.**
