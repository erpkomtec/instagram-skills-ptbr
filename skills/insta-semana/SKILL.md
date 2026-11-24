---
name: insta-semana
description: >-
  Rotina semanal do Instagram de ponta a ponta: lê os números, confere os
  testes da semana passada, faz a auditoria, monta o plano e deixa os rascunhos
  prontos para aprovação. Use quando pedirem "roda a semana do Instagram",
  "rotina do Instagram", "fecha a semana" ou quando uma tarefa agendada chamar.
---

# insta-semana

Liga as outras skills na ordem certa. **Termina em rascunho para aprovar,
nunca em publicação**, mesmo rodando agendada e sem ninguém olhando.

## A ordem

1. **Números.** Se houver navegador disponível e a pessoa já estiver logada,
   leia os Insights (7 e 30 dias e posts da semana), reaproveitando **uma aba só**.
   Não abra a página do post nem o Reel: abrir soma visualização. Só leitura: não curta,
   não comente, não envie, não mude nada. **Confira se a conta aberta é a do
   `voz.md`**; se não for, pare a coleta. Página só com títulos ainda está
   carregando: leia de novo, até três vezes. Pediu login ou confirmação? Pare a
   coleta e anote. Sem navegador, use o que estiver em
   `~/instagram-dados/metricas.tsv` e **diga a data do dado mais novo**.
   Acrescente as leituras novas; nunca reescreva as antigas.
2. **Testes anteriores.** Abra `testes.md`: deu certo, não deu ou falta dado?
3. **Auditoria.** Siga a `/insta-auditoria`.
4. **Pautas.** Se `pautas.md` tiver menos de cinco não usadas, siga a parte de
   dúvidas reais da `/insta-pesquisa`. Sem pessoa presente para responder,
   registre a pergunta e continue.
5. **Plano.** Siga a `/insta-plano`.
6. **Rascunhos.** Só dos dois primeiros itens do plano: `/insta-reel` ou
   `/insta-carrossel` (texto, sem gerar imagem), `/insta-legenda` e
   `/insta-humano`.
7. **Relatório** em `~/instagram-dados/semanas/AAAA-MM-DD.md`.

## O relatório, uma página

Números e variação · testes conferidos · o gargalo e a confiança · MANTER,
CORRIGIR, REPETIR ou PARAR · plano com horas · rascunhos · **o que a pessoa
precisa decidir** · o que não foi possível ler.

Se os números não mudaram ou não puderam ser lidos, diga isso em destaque. Não
invente análise para preencher.

## Agendar

Precisa do computador ligado se for ler arquivos locais. O agendamento é
criado pela pessoa, ou com a autorização dela. Uma vez por semana basta.
