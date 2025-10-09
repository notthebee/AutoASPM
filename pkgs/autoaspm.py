#!/usr/bin/env python3

import re
import subprocess
import os
import platform
import argparse
from enum import Enum


class ASPM(Enum):
    DISABLED = 0b00
    L0s = 0b01
    L1 = 0b10
    L0sL1 = 0b11


def run_prerequisites():
    if platform.system() != "Linux":
        raise OSError("This script only runs on Linux-based systems")
    if not os.environ.get("SUDO_UID") and os.geteuid() != 0:
        raise PermissionError("This script needs root privileges to run")
    for cmd in ["lspci", "setpci"]:
        if subprocess.run(["which", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode > 0:
            raise Exception(f"{cmd} not detected. Please install pciutils")


def get_device_name(addr):
    """Return the lspci description for a given PCI address"""
    p = subprocess.Popen(["lspci", "-s", addr], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.communicate()[0].splitlines()[0].decode().strip()


def read_all_bytes(device):
    all_bytes = bytearray()
    device_name = get_device_name(device)
    p = subprocess.Popen(["lspci", "-s", device, "-xxx"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret = p.communicate()[0].decode()
    for line in ret.splitlines():
        if not device_name in line and ": " in line:
            all_bytes.extend(bytearray.fromhex(line.split(": ")[1]))
    if len(all_bytes) < 256:
        exit()
    return all_bytes


def find_byte_to_patch(bytes, pos):
    pos = bytes[pos]
    if bytes[pos] != 0x10:
        pos += 0x1
        return find_byte_to_patch(bytes, pos)
    else:
        pos += 0x10
        return pos


def patch_byte(device, position, value, dry_run=False):
    """Write a byte via setpci unless dry_run is True"""
    if dry_run:
        print(f"[DRY-RUN] Would run: setpci -s {device} {hex(position)}.B={hex(value)}")
    else:
        subprocess.Popen(["setpci", "-s", device, f"{hex(position)}.B={hex(value)}"]).communicate()


def patch_device(addr, aspm_value, verbose=False, dry_run=False):
    endpoint_bytes = read_all_bytes(addr)
    byte_position_to_patch = find_byte_to_patch(endpoint_bytes, 0x34)
    device_name = get_device_name(addr)

    current_value = int(endpoint_bytes[byte_position_to_patch]) & 0b11
    target_value = aspm_value.value

    if current_value != target_value:
        patched_byte = int(endpoint_bytes[byte_position_to_patch])
        patched_byte = (patched_byte >> 2) << 2 | target_value
        patch_byte(addr, byte_position_to_patch, patched_byte, dry_run=dry_run)
        msg = f"{addr}: Enabled ASPM {aspm_value.name}"
    else:
        msg = f"{addr}: Already has ASPM {aspm_value.name} enabled"

    if verbose:
        print(f"{addr} ({device_name}): {msg.split(': ')[1]}")
    else:
        print(msg)


def list_supported_devices():
    """Return a dict {addr: (aspm_mode, description)}"""
    pcie_addr_regex = r"([0-9a-f]{2}:[0-9a-f]{2}\.[0-9a-f])"
    lspci = subprocess.run("lspci -vv", shell=True, capture_output=True).stdout
    lspci_arr = re.split(pcie_addr_regex, str(lspci))[1:]
    lspci_arr = [x + y for x, y in zip(lspci_arr[0::2], lspci_arr[1::2])]

    aspm_devices = {}
    for dev in lspci_arr:
        device_addr = re.findall(pcie_addr_regex, dev)[0]
        if "ASPM" not in dev or "ASPM not supported" in dev:
            continue
        aspm_support = re.findall(r"ASPM (L[L0-1s ]*),", dev)
        if aspm_support:
            desc = get_device_name(device_addr)
            aspm_devices.update({device_addr: (ASPM[aspm_support[0].replace(" ", "")], desc)})
    return aspm_devices


def main():
    parser = argparse.ArgumentParser(description="PCIe ASPM patching utility")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed device info")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Do not make any changes, only show actions")
    args = parser.parse_args()

    run_prerequisites()
    devices = list_supported_devices()

    if args.verbose:
        print("Detected ASPM-capable devices:\n")
        for device, (aspm_mode, desc) in devices.items():
            print(f"{device} - {desc} (ASPM: {aspm_mode.name})")
        print("\n--- Starting ASPM patching ---")

    for device, (aspm_mode, _) in devices.items():
        patch_device(device, aspm_mode, verbose=args.verbose, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
