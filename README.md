# instagram-skills-ptbr

Skills do [Claude](https://claude.ai) para criar conteúdo de Instagram **em
português do Brasil**: 14 skills que vão da auditoria do perfil ao roteiro
de Reel com tempo por sílaba, carrossel em PNG, legenda, Stories, respostas e
o plano da semana.

**Não posta nada, não pede senha e não usa API da sua conta.** As skills
escrevem e conferem; quem grava e publica é você. Os scripts rodam no seu
computador, só com Python, sem internet e sem instalar biblioteca. Para ler
métricas, o Claude pode usar o navegador que **você** deixou logado, só leitura.

Mantido pela equipe do [ERP KomTec Pro](https://erpkomtec.com.br), que usa
estas skills para roteirizar os próprios vídeos de demonstração.

---

## Por que existe

Adaptamos o excelente
[instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill),
de Jake Schincariol (licença MIT), que é todo pensado para inglês. Em português
ele quebrava em pontos básicos:

| No original (inglês) | Aqui (pt-BR) |
|---|---|
| `Não perca orçamento.` contava **5 palavras** (o acento partia a palavra) | conta 3 |
| Tempo estimado por palavras por minuto | tempo por **sílabas**: "é" e "configuração" não levam o mesmo tempo |
| Não reconhecia `R$ 1.250,00`, "mil", "reais", "prejuízo" | reconhece valores, números falados e palavras de dinheiro |
| Ganchos e aberturas fracas só em inglês | 26 fórmulas reescritas com exemplos brasileiros; "Oi, pessoal" e "Nesse vídeo vou mostrar" eliminam |
| — | **.srt** das falas e das cartelas para importar no CapCut |
| — | **moldura 9:16** em PNG com a área que a interface do Instagram cobre |
| — | **calibragem** do seu ritmo de fala (`--calibrar`) |
| Sem testes | 51 testes automáticos |

## O que tem (v0.2)

| Comando | O que faz |
|---|---|
| `/insta-semana` | A rotina completa: números, auditoria, plano e rascunhos para aprovar |
| `/insta-auditoria` | O que funcionou e onde trava, contra a mediana do seu perfil |
| `/insta-pesquisa` | Dúvidas reais + Reels do nicho viram um banco de pautas |
| `/insta-plano` | A semana dentro das horas que você tem |
| `/insta-reel` | Da ideia ao roteiro: ganchos com nota, fala, cartelas, tempos e `.srt` |
| `/insta-carrossel` | Texto e imagens PNG 1080x1350 |
| `/insta-legenda` | Escreve e confere a legenda |
| `/insta-stories` | Sequência do dia, quadro a quadro |
| `/insta-perfil` | Nota do perfil em 12 itens e reescrita |
| `/insta-humano` | Tira o jeito de texto de IA em português |
| `/insta-comentario` | Comentários em posts de outras contas |
| `/insta-resposta` | Separa e responde os comentários recebidos |
| `/insta-direct` | Direct, convite de collab e caminho até a venda |
| `/insta-reaproveitar` | Um conteúdo longo vira várias peças |

Scripts que o Claude roda (e você também pode rodar na mão):

```
skills/insta-reel/gancho.py          nota do gancho (0-100) em 5 propriedades
skills/insta-reel/tempos.py          tempos por sílaba, .srt de fala e de tela, calibragem
skills/insta-reel/moldura.py         PNG 1080x1920 com a área segura
skills/insta-legenda/legenda.py      conferência da legenda
skills/insta-auditoria/auditoria.py  múltiplo sobre a mediana, gargalo e confiança
skills/insta-pesquisa/pesquisa.py    Reels do nicho pelo múltiplo da própria conta
skills/insta-humano/humano.py        limpa tipografia e aponta expressões batidas
skills/insta-carrossel/carrossel.py  confere os slides e gera os PNG (Chrome ou Edge)
```

## Instalação

**Precisa de:** [Claude Code](https://claude.com/claude-code) e Python 3.8 ou mais novo.

**Como plugin (mais fácil):** dentro do Claude Code,

```
/plugin marketplace add erpkomtec/instagram-skills-ptbr
/plugin install instagram-skills-ptbr
```

**Manual:** clone o repositório e rode `python instalar.py`. Ele copia as pastas
`skills/insta-*` para `~/.claude/skills/` e guarda a cópia anterior. Rode de novo
a cada atualização.

**Sem Claude Code:** cole o conteúdo de um `SKILL.md` numa conversa com o
Claude. Os scripts ficam de fora, mas as instruções funcionam.

**Depois, uma vez só:** copie `modelos/voz.md` para `~/instagram-dados/voz.md`
e preencha (ou mande três vídeos seus ao Claude e peça para ele preencher).
Todas as skills leem esse arquivo. (Até a v0.2.0 a pasta era
`~/.claude/instagram`; ela é protegida pelo Claude Code e travava a rotina
agendada. Se você já usava, mova os arquivos.) **Ele é pessoal: não suba para repositório
público.**

## Uso rápido

```
/insta-reel orçamento que levava 5 horas agora sai em 20 minutos
```

No roteiro, o texto que aparece na tela vai entre colchetes, na linha de cima
da fala:

```
[tela: 5 HORAS -> 20 MIN]
Orçamento que levava cinco horas agora sai em vinte minutos.
```

Rodando o script direto:

```bash
python skills/insta-reel/tempos.py roteiro.txt --alvo 30 --srt-fala fala.srt --srt-tela tela.srt
python skills/insta-reel/gancho.py --gancho "Pare de montar orçamento no Word."
python skills/insta-legenda/legenda.py legenda.txt --buscas "sistema para oficina"
```

No CapCut: **Texto → Legendas → Importar** e escolha o `.srt`.

## Limites, com honestidade

- **A nota do gancho não prevê viralização.** No teste do autor original (74
  ganchos, em inglês), ela separou bem gancho ruim de gancho bom, mas não
  acertou qual vídeo de um mesmo criador ia performar melhor. A versão em
  português ainda não foi medida. Use para **descartar o fraco**.
- **Sílabas são contadas por aproximação** (grupos de vogais). Hiatos como
  "saída" contam uma a menos. A margem é pequena e a calibragem compensa.
- **As medidas da área segura** mudam um pouco entre celulares e versões do
  aplicativo. São margem de segurança, não encaixe exato.
- **Nenhuma skill inventa número.** Se falta um dado, o roteiro volta com
  `{{seu número}}`.
- **A auditoria levanta hipóteses.** Os limites dela são ponto de partida, não
  regra do Instagram, e com menos de 10 posts ela mesma avisa que não conclui.
- **`/insta-humano` não é detector de IA** e não serve para esconder uso de IA: o
  rótulo do Instagram continua valendo.
- **Robô que comenta, segue ou dispara direct** viola os termos do Instagram e
  pode bloquear a conta. Por isso não existe aqui. Publicar pela API oficial da
  Meta é permitido, mas exige aplicativo próprio e fica fora deste projeto.

## Próximos passos

- [ ] `/insta-tela`: roteiro de gravação de tela de sistema (tela, clique, zoom por fala)
- [ ] medir a nota do gancho com Reels brasileiros reais

## Testes

```bash
python -m unittest discover -s testes -v
```

## Contribuindo

Sugestões e correções são bem-vindas por *issue* ou *pull request*. É um
projeto mantido no tempo livre: não há prazo de resposta nem suporte garantido.

## Licença e créditos

MIT. Obra original © 2026 Jake Schincariol
([instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill)).
Adaptação para o português e acréscimos © 2026 ERP KomTec Pro. Veja `LICENSE`.
