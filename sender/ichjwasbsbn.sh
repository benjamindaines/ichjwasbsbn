#!/bin/bash
set -u
# Create a vairable in whatever script you want to use this with, point it to this script,
# then call it with an argument that is the content of your notification.  I drop the .sh
# extension and put it in ~/.local/bin/ but the extension makes it more clear that you
# should open and edit this file.  
#
# Set envFile here:
envFile=/home/<user>/.config/ichjwasbsbn.token



# The rest of this shouldn't need editing, unless you just want to...

TOKEN=$(sed -n 's/^NOTIFY_TOKEN=//p' "$envFile")
PORT=8765
HOST=${SSH_CONNECTION%% *}
BODY=${1:-}

if [ ! -r "$envFile" ]; then
	printf "Token file expected at %s is missing.  Cannot proceed.\n" "$envFile" >%2
	exit 1
fi

if [[ $(stat -c '%a' "$envFile") != 600 ]]; then
	printf "WARNING: DBus token file permissions allow other users to write to it.  Halting to prevent possible execution of arbitrary code.  Verify the authenticity of %s and fix your permissions." "$envFile" >%2
	exit 1
fi

LINE=$(printf "%s\t%s" "$TOKEN" "$BODY")

timeout 3 python3 - "$HOST" "$PORT" "$LINE" <<'PY' 2>/dev/null || true
import socket, sys
host, port, line = sys.argv[1], int(sys.argv[2]), sys.argv[3]
with socket.create_connection((host, port), timeout=3) as s: s.sendall((line + "\n").encode())
PY
