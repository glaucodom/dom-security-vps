#!/usr/bin/env python3
"""Inventário parcial de VPS Linux: somente leitura; saída privada e sem rede externa."""
import argparse
import datetime
import json
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import sys
import time

TRUSTED_PATH = '/usr/sbin:/usr/bin:/sbin:/bin'
LIMIT = 128 * 1024


def run(argv, timeout=8, limit=LIMIT):
    started = time.monotonic()
    exe = shutil.which(argv[0], path=TRUSTED_PATH)
    result = {'command': argv, 'status': 'missing', 'returncode': None,
              'truncated': False, 'output': ''}
    if not exe:
        return result
    data = bytearray()
    try:
        with subprocess.Popen([exe] + argv[1:], stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              env={'PATH': TRUSTED_PATH, 'LANG': 'C', 'LC_ALL': 'C'},
                              close_fds=True) as proc:
            sel = selectors.DefaultSelector()
            try:
                sel.register(proc.stdout, selectors.EVENT_READ)
                status = 'completed'
                while True:
                    if time.monotonic() - started >= timeout:
                        status = 'timeout'
                        break
                    if not sel.select(timeout=min(0.1, max(0, timeout - (time.monotonic() - started)))):
                        continue
                    block = os.read(proc.stdout.fileno(), min(8192, limit - len(data) + 1))
                    if not block:
                        break
                    data.extend(block)
                    if len(data) > limit:
                        del data[limit:]
                        result['truncated'] = True
                        status = 'output_limit'
                        break
                if status != 'completed':
                    proc.kill()
                try:
                    rc = proc.wait(timeout=max(0.1, timeout - (time.monotonic() - started)))
                except subprocess.TimeoutExpired:
                    status = 'timeout'
                    proc.kill()
                    rc = proc.wait()
                result.update(status=status if status != 'completed' or rc == 0 else 'failed',
                              returncode=rc, output=data.decode('utf-8', errors='replace'))
            finally:
                sel.close()
    except OSError as exc:
        result.update(status='error', output=type(exc).__name__ + ': ' + str(exc))
    result['duration_seconds'] = round(time.monotonic() - started, 3)
    return result


def collect(include_docker=False):
    checks = [
        ['uname', '-srmo'],
        ['id'],
        ['uptime'],
        ['df', '-h', '-x', 'tmpfs', '-x', 'devtmpfs'],
        ['free', '-m'],
        ['ss', '-H', '-lntu'],
        ['ps', '-eo', 'pid,ppid,uid,comm', '--sort=pid'],
        ['systemd-detect-virt'],
        ['systemctl', 'list-units', '--type=service', '--state=running', '--no-pager', '--plain'],
        ['systemctl', 'list-units', '--state=failed', '--no-pager', '--plain'],
        ['systemctl', 'list-timers', '--all', '--no-pager', '--plain'],
        ['sshd', '-t'],
        ['ufw', 'status', 'verbose'],
        ['firewall-cmd', '--state'],
        ['nft', 'list', 'ruleset'],
        ['iptables', '-S'],
        ['ip6tables', '-S'],
    ]
    if include_docker:
        checks += [['docker', 'version', '--format', '{{.Server.Version}}'],
                   ['docker', 'ps', '--format', '{{.ID}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}']]
    try:
        with open('/etc/os-release', encoding='utf-8') as stream:
            release = stream.read(16384)
    except OSError as exc:
        release = type(exc).__name__ + ': ' + str(exc)
    return {'schema_version': 1,
            'started_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'euid': os.geteuid(), 'os_release': release,
            'scope': 'partial-local-read-only-inventory',
            'limitations': ['Não detecta ou exclui invasão.',
                            'Não consulta CVEs nem examina logs, contas, chaves, código ou backups.',
                            'Não valida exposição externa nem firewall do provedor.',
                            'Resultados dependem dos privilégios e da integridade das ferramentas locais.',
                            'Saída contém metadados sensíveis; não publicar.',
                            'Comandos podem gerar logs; arquivo de saída é a única escrita intencional.'],
            'checks': [run(command) for command in checks],
            'finished_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='Arquivo novo em diretório privado existente, fora de Git/webroot')
    parser.add_argument('--docker', action='store_true', help='Consultar somente metadados de containers via Docker local')
    args = parser.parse_args()
    if not sys.platform.startswith('linux'):
        parser.error('Este coletor requer Linux.')
    output = Path(args.output).absolute()
    try:
        # O_EXCL impede sobrescrita e seguir symlink no arquivo final.
        fd = os.open(str(output), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except OSError as exc:
        parser.error('Não foi possível criar a saída privada: ' + str(exc))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(collect(args.docker), stream, ensure_ascii=False, indent=2)
            stream.write('\n')
    except BaseException:
        # Preservar saída parcial para diagnóstico; não alegar sucesso.
        print('Coleta incompleta; conferir arquivo parcial privado.', file=sys.stderr)
        raise
    print('Inventário parcial salvo. Revisar limitações e sanitizar antes de compartilhar.')


if __name__ == '__main__':
    main()
