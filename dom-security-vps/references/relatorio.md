# Modelo de relatório sanitizado

## Resultado

Data/hora UTC; alvo com identificador sanitizado; ambiente; modo; escopo e autorização; acesso/privilégios; sintomas; conclusão com limites. Separar inventário automático da análise humana/agente. “Não identifiquei sinais nas verificações realizadas” nunca significa “não houve invasão”.

## Cobertura

| Camada | Estado | Evidência resumida | Limitação |
|---|---|---|---|
| SSH | Verificado/achado/não aplicável/não verificado | Sem segredos | Contextos não testados |

Enumerar todas as camadas aplicáveis da matriz, inclusive as sem acesso.

## Achados

| ID | Prioridade | Confiança | Alvo | Evidência sanitizada | Impacto | Ação |
|---|---|---|---|---|---|---|

Para cada achado, detalhar comando/fonte e horário, observação vs inferência, exposição, CVE/advisory com data quando houver, risco de exploração, correção, teste e risco residual. Não expor senhas, tokens, chaves, cookies, dados pessoais, logs completos ou hashes de senha.

Priorizar como P0: comprometimento confirmado em andamento ou dano iminente fundamentado; P1: risco crítico com exposição e pré-requisitos plausíveis; P2: risco importante sem urgência demonstrada; P3: melhoria. Ajustar ao impacto real, sem equiparar presença no KEV a prova de exploração nesta VPS.

## Plano e execução

| Ação | Pré-requisito | Impacto | Autorização | Backup/rollback | Teste | Estado |
|---|---|---|---|---|---|---|

Separar proposto, autorizado, executado, validado e revertido. Listar alterações exatas, falhas e pendências. Informar fontes oficiais consultadas e data das bases. Incluir limites do acesso, coleta truncada, comandos ausentes ou negados. Encerrar com próximo passo de maior prioridade e responsável se conhecido. Guardar relatório privado fora do Git.
