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
# Faz git pull e atualiza todos os arquivos + correções de segurança
python3 ./update/update.py
```

**O que o update faz:**
- ✅ Atualiza todos os arquivos Python com as correções
- ✅ Tenta atualizar as regras sudoers (requer sudo na primeira execução)
- ✅ Preserva suas configurações de host salvas

**Se as regras sudoers não forem atualizadas automaticamente:**
```bash
sudo ./installer/install.sh  # Reinstalação completa
```

## Segurança

Este projeto implementa as seguintes medidas de segurança:

- ✅ Validação rigorosa de entrada (formato de host)
- ✅ Proteção contra command injection
- ✅ Regras sudoers restritivas
- ✅ Gerenciamento automático de DNS
- ✅ Backup e restauração de configurações

Para mais detalhes, consulte `SECURITY.md`.
