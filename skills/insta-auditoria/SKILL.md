---
name: insta-auditoria
description: >-
  Analisa o que já foi postado no Instagram: o que funcionou, o que parar de
  fazer e onde trava (gancho, alcance ou perfil), medindo cada post contra a
  mediana do próprio perfil. Use quando pedirem "analisa meu Instagram", "o que
  está funcionando", "por que esse Reel não foi", "lê meus insights", "audita
  meus posts" ou colarem prints de métricas.
---

# insta-auditoria

A única fonte honesta do que funciona numa conta é a própria conta.

```bash
python auditoria.py ~/instagram-dados/metricas.tsv
```

## De onde vêm os números

Na ordem: o arquivo `~/instagram-dados/metricas.tsv`, prints que a pessoa
mandar, ou os Insights lidos no navegador **já logado por ela**, com ela
sabendo. Nunca peça senha nem faça login. Só leia: não curta, não comente,
não clique em publicar.

Alguns números (como a retenção) podem aparecer só no aplicativo do celular.
Se não encontrar, peça um print. Anote cada leitura no TSV, com a coluna
`horas` (idade do post na leitura). **Célula desconhecida fica vazia, nunca
zero**, e só entra número lido na tela: nada deduzido por conta ou eliminação.
Use sempre o mesmo nome de post; a última linha de cada nome é a que vale. As colunas estão no topo do `auditoria.py`.

Leia também `~/instagram-dados/registro.md`, que diz qual fórmula de gancho
cada post usou.

## O que medir

| Medida | Conta | O que diz |
|---|---|---|
| Múltiplo | visualizações / mediana do perfil | se foi acima do normal |
| % não seguidores | vem dos Insights | se saiu da bolha |
| Retenção em 3 s | quem ficou / quem começou | a nota real do gancho |
| Envios por alcance | compartilhamentos / alcance | se valeu mandar para alguém |
| Seguidores por alcance | novos / alcance | se o perfil converteu |

Interações de contas próprias, da família e da equipe inflam conta pequena.
Pergunte quantas são e diga isso no relatório.

## Como concluir

1. Rode o script e mostre a saída, com a confiança que ele calculou.
2. Compare o terço de cima com o de baixo: gancho, formato, duração, tema.
   Dia e horário por último, e só se o resto não explicar.
3. Separe **observado** (está no número) de **hipótese** (falta testar).
4. Pouca visualização costuma ser gancho. Visualização sem seguidor novo
   costuma ser perfil. Descubra qual antes de receitar.
5. Classifique: **REPETIR, CORRIGIR ou PARAR**. Com menos de 10 posts
   maduros, só hipóteses.
6. Feche com até três testes: o que muda, qual métrica, valor de hoje, o que
   conta como sucesso e quando conferir. Uma mudança por teste.

Grave os testes em `~/instagram-dados/testes.md` e, na auditoria seguinte,
comece conferindo os anteriores.

## Regras

- Nunca invente métrica. O que falta vai na lista do que falta.
- Os limites do script são ponto de partida, não regra do Instagram.
- Não prometa alcance nem venda.
