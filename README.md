# JS VPN

Aplicativo para conectar e desconectar VPN usando openconnect.

## ⚠️ Importante - Migração de Repositório

Este projeto deve ser migrado para o repositório corporativo por questões de segurança.

# Sistemas Compatíveis:

- Linux Mint
- Ubuntu
- Debian
- Pop!_OS
- Zorin OS

## Instalar

```bash
chmod +x installer/install.sh
sudo ./installer/install.sh
```

Depois procure por `JS VPN` no menu de aplicativos do seu linux.

O app inicia automaticamente ao entrar no Linux.

## Atualização

O sistema de atualização agora inclui correções de segurança automáticas:

```bash
# Atualiza a instalação com os arquivos deste checkout
python3 ./update/update.py
```

Para atualizar somente o aplicativo, mantendo as regras sudoers existentes:

```bash
python3 ./update/update.py --skip-sudoers
```

**O que o update faz:**
- ✅ Atualiza todos os arquivos Python com as correções
- ✅ Tenta atualizar as regras sudoers (requer sudo na primeira execução)
- ✅ Preserva suas configurações de host salvas

**Se as regras sudoers não forem atualizadas automaticamente:**
```bash
sudo ./installer/install.sh  # Reinstalação completa
```

## Autenticação SAML

O aplicativo autentica diretamente no gateway, mantendo o login Microsoft e o
Authenticator. O cookie é capturado em memória e enviado ao OpenConnect pela
entrada padrão, sem aparecer no terminal ou nos argumentos do processo.

O host informado deve atender à autenticação do gateway. Se o endereço atual for
exclusivo do portal, informe o host do gateway disponibilizado pela empresa.

Para comparar o fluxo pelo portal, execute a partir deste checkout:

```bash
python3 -m js_vpn.auth --portal vpn-guest.fiesc.com.br
```

Também é possível testar a política de sistema operacional do gateway:

```bash
python3 -m js_vpn.auth --clientos=Windows vpn-guest.fiesc.com.br
```

## Segurança

Este projeto implementa as seguintes medidas de segurança:

- ✅ Validação rigorosa de entrada (formato de host)
- ✅ Proteção contra command injection
- ✅ Regras sudoers restritivas
- ✅ Gerenciamento automático de DNS
- ✅ Backup e restauração de configurações

Para mais detalhes, consulte `SECURITY.md`.
