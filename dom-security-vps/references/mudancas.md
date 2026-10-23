# Mudanças e reversão

Para cada lote autorizado registrar alvo, finalidade, comandos/diff, impacto, pré-requisitos, backup, teste, rollback e critério de interrupção. Armazenar cópias com permissões restritas fora de webroot/Git. Revisar e validar rollback antes da alteração. Não usar caminhos exemplificativos como caminhos reais. Não repetir aprovação se já cobrir o lote concreto.

## SSH e firewall

- Confirmar IP/origem e porta efetivos, autenticação válida, contas de serviço, VPN e regras IPv4/IPv6. Garantir console do provedor e segunda sessão independente. Não aplicar bloqueios sem alternativa de recuperação demonstrável.
- Não desabilitar senha/root até testar conta alternativa com chave e elevação necessária. Preservar automações autorizadas. Alterar porta não substitui autenticação e controles de acesso.
- Fazer backup e validar candidato com `sshd -t -f CAMINHO_REAL`; verificar configuração efetiva com `sshd -T` e contextos `-C` que contemplem Match. Confirmar includes, prioridade e como o serviço realmente inicia. Não considerar somente grep do arquivo principal.
- Usar reload compatível em vez de restart quando apropriado; testar nova sessão mantendo a anterior. Identificar socket activation. Não fechar sessão original antes de validar.
- No firewall, incluir acesso administrativo antes da política de negação. Preparar reversão temporizada específica com mecanismo disponível e autorizado; confirmar sua execução possível e cancelar somente após teste externo e nova sessão. Não usar `iptables -F`, `nft flush ruleset`, `ufw reset`, desativar firewall ou liberar tudo como rollback padrão.

## Pacotes, código e containers

- Conferir EOL, backports e avisos da distro. Separar atualizar índice, instalar pacote, reiniciar serviço e reboot: cada um tem impacto próprio. Pacote pode reiniciar serviço em pós-instalação. Planejar janela e restauro; downgrade pode não ser viável.
- Não executar atualização geral, major, `npm audit fix --force`, scripts de dependências ou migrations em produção automaticamente. Atualização minor/patch também pode quebrar comportamento.
- Em cópia isolada, usar lockfile e testes relevantes. Não conectar testes a banco, pagamentos, filas, e-mail ou endpoints reais. Desativar integrações de forma verificável.
- Pinagem de imagens e digest; preservar volumes, mounts, networks, healthchecks e versão anterior. Nunca executar `docker system prune`, remover volumes, `compose down -v` ou recriar stack sem plano de dados e autorização específica.
- Validar configuração do proxy antes de reload. Após mudança, conferir HTTP/TLS, autenticação, tarefas, filas, integrações e métricas. Se falhar, interromper e reverter conforme plano; não ocultar falhas.

## Banco, credenciais e recuperação

Validar backup consistente e restauração isolada. Preparar manutenção e compatibilidade para mudanças de banco; não pressupor reversibilidade de schema. Rotação exige atualização coordenada de consumidores e revogação; não colocar segredo em shell history, argumentos, logs ou Git. Não reutilizar senha comprometida para rollback. Testar que dados e serviços continuam acessíveis somente a identidades autorizadas.
