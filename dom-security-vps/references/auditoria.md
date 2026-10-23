# Matriz de auditoria

Executar apenas verificações compatíveis com o ambiente. Começar pelos metadados; aprofundar arquivos e logs somente no escopo necessário, com limites de tempo/volume. Evitar recursão de todo o disco, caminhos virtuais, volumes enormes e redes montadas. Não elevar privilégios automaticamente. Resultados podem conter IPs, usuários, domínios e identificadores: sanitizar a apresentação.

| Camada | Verificar | Evidências e limites |
|---|---|---|
| Provedor | MFA, recuperação, chaves API, colaboradores, firewall/security groups, snapshots, console de emergência | API/painel autorizado; sem acesso, não verificado |
| SO | Distribuição, suporte, avisos de segurança, pacotes e kernel em execução, necessidade de reboot, disco | `/etc/os-release`, `uname -r`, gerenciador nativo; cache pode estar desatualizado; não executar upgrade ou refresh implicitamente |
| Identidades | UID 0 adicionais, sudoers e includes, contas interativas/inativas, grupos privilegiados, acessos de deploy | Metadados necessários; não coletar hashes de senha nem conteúdo de `/etc/shadow` |
| SSH | Configuração efetiva, includes/Match, root/senhas/chaves/MFA, usuários permitidos, forwarding necessário, porta/endereço e socket activation | `sshd -t`; `sshd -T` e contextos `-C` reais; negar root/senha só após testar alternativa; não confundir fail2ban com autenticação segura |
| Rede | TCP/UDP em IPv4/IPv6, bind, reverse proxy, VPN, portas de administração, DNS, saída suspeita | `ss`, backend real nftables/iptables/firewalld/UFW e firewall do provedor; validar externamente somente com autorização |
| Serviços | Serviços ativos/falhos, timers, cron, inicialização, privilégios e perfis AppArmor/SELinux | Metadados primeiro; investigar units/drop-ins e cron selecionados, sem publicar comandos que contenham segredos |
| Persistência/incidente | Mudanças em chaves, usuários, units, cron, caminhos de upload, executáveis temporários e conexões incomuns | Correlacionar com deploy e logs; arquivo recente ou alto CPU sozinho não prova invasão; não executar conteúdo suspeito |
| Docker | Engine/API/socket, acesso ao grupo docker, portas publicadas, root/privileged, capabilities, host namespaces, mounts host, imagens/digests e redes | `docker ps` com formato restrito e inspeção de campos selecionados; nunca dump de inspect/Env completo; socket/root do host são privilégios críticos |
| Coolify/Portainer | Versão/suporte, painel exposto, MFA se disponível, contas/tokens, webhooks, proxy, secrets, backups e controle de deploy | Conferir documentação da versão; não alterar redes, portas ou volumes geridos pelo painel sem entender dependências |
| Proxy/TLS | Certificado/cadeia/expiração, renovação, TLS, rotas administrativas, cabeçalhos/cookies e limites apropriados | Nginx/Apache/Caddy/Traefik conforme instalado; testes de sintaxe antes de reload; HSTS/CSP exigem compatibilidade e podem quebrar clientes |
| Aplicação | Autenticação/autorização, isolamento por empresa, upload/path traversal, injeção, SSRF, execução de comandos, CSRF, CORS, rate limiting, debug e arquivos públicos | Revisão dirigida nos caminhos autorizados; nenhuma exploração em produção; não confundir ausência de achado com teste completo |
| Dependências | Lockfiles PHP/JS e outros ecossistemas presentes, versões efetivas, advisories, dev/prod, runtime PHP/Node e EOL | Auditores nativos e scanner apropriado em cópia isolada; `npm audit fix --force` proibido; WordPress core/plugins/temas requerem análise própria |
| Dados/segredos | Bind/rede de Postgres/MySQL/Redis, autenticação/TLS/ACL, permissões mínimas, arquivos e secrets, histórico Git no escopo | Não ler registros de clientes, `.env`, hashes ou tokens; scanner com redação; Redis/Postgres expostos exigem contexto, não só número da porta |
| Backups | Cópia independente/offline ou imutável quando viável, criptografia, credenciais separadas, retenção, RPO/RTO e restauração | Confirmar teste em destino isolado sem sobrescrever produção; backup acessível pelo atacante não é proteção suficiente |
| Detecção | Logs de auth/proxy/app, retenção, rotação, integridade, sincronismo, alertas e monitoramento externo | Não enviar logs a terceiros sem autorização; alertar em falha de coleta, não declarar tudo limpo |

## Docker e firewall

Não concluir que `ufw active` protege portas publicadas. Docker pode encaminhar tráfego antes das regras INPUT/OUTPUT do UFW. Identificar backend e versão. Usar o mecanismo documentado adequado: DOCKER-USER no backend iptables quando aplicável, ou a abordagem nftables suportada pela versão; não copiar regras entre backends. Não desativar a gestão de firewall do Docker nem dar flush em regras. Considerar Swarm, redes host/macvlan, portas locais, roteamento direto e IPv6. Conferir também firewall do provedor.

## Dependências e ferramentas

Registrar comandos, versão do scanner e data das bases. `npm audit`/Composer/OSV e scanners podem enviar nomes/versões ou buscar bases pela rede; comunicar o destino quando houver transmissão e respeitar restrições. Ferramentas em repositórios podem executar código: preferir binários confiáveis e cópia isolada, sem scripts/hooks/plugins do projeto nem secrets. Não instalar WP-CLI/plugin para mera auditoria sem autorização. Dependência não usada pode continuar sendo risco; analisar alcance sem descartar automaticamente.

## Fontes oficiais para consulta atual

- OpenSSH: https://man.openbsd.org/sshd e https://man.openbsd.org/sshd_config
- Docker: https://docs.docker.com/engine/network/packet-filtering-firewalls/
- Ubuntu: https://ubuntu.com/security/notices
- Debian: https://security-tracker.debian.org/tracker/
- Red Hat: https://access.redhat.com/security/security-updates/
- CISA KEV: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- OSV: https://osv.dev/ ; GitHub Advisory Database: https://github.com/advisories
- Coolify: https://coolify.io/docs/
- Trivy: https://trivy.dev/ ; Grype: https://github.com/anchore/grype
- Lynis: https://cisofy.com/lynis/ ; Gitleaks: https://github.com/gitleaks/gitleaks

Conferir a documentação da versão local; URLs de referência não substituem a verificação atual nem constituem dependências instaladas.
