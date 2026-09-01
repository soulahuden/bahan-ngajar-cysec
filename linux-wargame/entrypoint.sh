#!/bin/bash
set -e

# generate SSH host key jika belum ada (misalnya setelah volume baru)
ssh-keygen -A

# jalankan sshd di foreground supaya container tetap hidup
exec /usr/sbin/sshd -D -e
