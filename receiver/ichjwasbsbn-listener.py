#!/usr/bin/env python3
"""
ichjwasbsbn — I could have just written a simple bash script, but no

Allows bash scripts to send notifications to your local KDE Environment
(probably other DEs too) via DBus when running on a remote host.
"""

import os
import socket
import subprocess
import sys

# --- configuration ---------------------------------------------------------
ALLOWED_IP  = "192.168.0.9"   # remote machine's static IP (the only allowed peer)
LISTEN_HOST = "0.0.0.0"       # interface to bind listening service to
LISTEN_PORT = 8765            # arbitrary port. don't pick anything already used
MAX_BYTES   = 2048            # limit message size 
REMOTE_HOST = "Server"        # fixed title — Host name of the remote machine makes sense
TOKEN_REQ   = "true"          # set to enforce token usage
TOKEN       = os.environ.get("NOTIFY_TOKEN") # see the .token files  
# ---------------------------------------------------------------------------


def sanitize(text: str) -> str:
    text = text.replace("\r", " ").replace("\n", " ")
    text = "".join(ch for ch in text if ch == " " or ch.isprintable())
    text = text.strip()
    return text[:300] if text else "(empty message)"


def notify(body: str) -> None:
    subprocess.run(
        [
            "notify-send",
            "--urgency=critical",        # critical keeps notification on screen until dismissed manually 
            "--app-name=remote-build",
            "--icon=dialog-information",
            "--",                        
            SUMMARY,
            body,
        ],
        check=False,
    )


def handle(conn: socket.socket) -> None:
    conn.settimeout(5)
    chunks, received = [], 0
    while received < MAX_BYTES:
        try:
            data = conn.recv(1024)
        except socket.timeout:
            break
        if not data:
            break
        chunks.append(data)
        received += len(data)

    raw = b"".join(chunks).decode("utf-8", errors="replace")
    lines = raw.splitlines()
    raw = lines[0] if lines else ""

    if TOKEN is not None:
        prefix = TOKEN + "\t"
        if not raw.startswith(prefix):
            print("rejected: bad or missing token", file=sys.stderr)
            return
        raw = raw[len(prefix):]

    body = sanitize(raw)
    print(f"notifying: {body!r}", file=sys.stderr)
    notify(body)


def main() -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((LISTEN_HOST, LISTEN_PORT))
    s.listen(8)

    if TOKEN_REQ and not TOKEN:
        sys.exit("refusing to start: TOKEN_REQ is set, but no TOKEN provided.")

    print(
        f"listening on {LISTEN_HOST}:{LISTEN_PORT}; "
        f"accepting only {ALLOWED_IP}"
        + (" (token required)" if TOKEN else ""),
        file=sys.stderr,
    )

    while True:
        conn, addr = s.accept()
        try:
            if addr[0] != ALLOWED_IP:
                print(f"rejected connection from {addr[0]}", file=sys.stderr)
                continue
            handle(conn)
        except Exception as e:           # one bad client must never kill the daemon
            print(f"error handling {addr}: {e}", file=sys.stderr)
        finally:
            conn.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
