# I could have just written a simple bash script, but no
Small python listening daemon.  Allow sending DBus notifications over SSH.  I use it get notifications for remote-run bash scripts. 

## Installation
- Generate `NOTIFY_TOKEN`s for the remote and local machines (both need to have the same key).  See the .token files for instructions.
- Set preferences at the top of `ichjwasbsbn-listener.py` & stash it somewhere ('$HOME/.local/bin/' is my preference)
- Edit the `ichjwasbsbn-listener.service` with the location of the python script and the .token file
- Put the `.service` file into `$HOME/.config/systemd/user/` and run `$ systemctl --user daemon-reload && systemd --user enable --now ichjwasbsbn-listener.service`
- Stash the `ichjwasbsbn.sh` and `.token` files somewhere on the remote machine (`$HOME/.config/ichjwasbsbn.token` and `$HOME/.local/bin/ichjwasbsbn`)
- Call `ichjwasbsbn "Notification content goes here, as an argument"` on the remote machine and enjoy your notification on your local machine. 
