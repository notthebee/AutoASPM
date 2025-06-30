# AutoASPM

A Python script that automatically activates ASPM for all supported devices on Linux.

It parses the `lspci -vv` output to determine which ASPM level is supported by
a device (e.g. L0s, L0sL1 or L1).

### Dependencies

- pciutils
- python3

### Usage

```bash
sudo autoaspm.py
```

#### Automatially apply on boot
Copy the `auto-aspm.service` systemd service file into the `/etc/systemd/system/`-directory. Edit the file and change the `WorkingDirectory` to the directory where you have saved the `autoaspm.py` file and replace the path to the python3 interpreter and the path to the script on the `ExecStart` line. Once that is done, run `systemctl daemon-reload` to update systemd service definitions and then run `systemctl enable auto-aspm.service` to run the script on boot or `systemctl enable --now auto-aspm.service` to run now and on boot.

### Credits

- Luis R. Rodriguez for writing the original enable_aspm script:
  https://www.uwsg.indiana.edu/hypermail/linux/kernel/1006.2/02177.html
- z8 for his Python rewrite of the enable_aspm script: https://github.com/0x666690/ASPM
