# AutoASPM

A Python script that automatically activates ASPM for all supported devices on Linux.

It parses the `lspci -vv` output to determine which ASPM level is supported by
a device (e.g. L0s, L0sL1 or L1).

## Dependencies

- pciutils
- python3
- which

## Usage

### NixOS - Run once

```bash
sudo git run github:notthebee/AutoASPM
```

### NixOS - Install permanently

1. Add this repository to your flake.nix:

```nix
autoaspm = {
    url = "github:notthebee/AutoASPM/dev?shallow=true";
    inputs.nixpkgs.follows = "nixpkgs";
};
```

2. Import the AutoASPM Nix module in your `nixosConfiguration`:

```nix
modules = [
    self.inputs.autoaspm.nixosModules.default
];
```

3. Enable the AutoASPM service in your configuration:

```nix
services.autoaspm.enable = true;
```

4. ???
5. Profit

### Other Linux distributions

1. Clone this repository

2. Run `sudo pkgs/autoaspm.py`

## Credits

- Luis R. Rodriguez for writing the original enable_aspm script:
  https://www.uwsg.indiana.edu/hypermail/linux/kernel/1006.2/02177.html
- z8 for his Python rewrite of the enable_aspm script: https://github.com/0x666690/ASPM
