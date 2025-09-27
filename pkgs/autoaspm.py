#!/usr/bin/env python3

# Original bash script by Luis R. Rodriguez
# Re-written in Python by z8
# Re-re-written to patch supported devices automatically by notthebee

import re
import subprocess
import os
import platform
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
    lspci_detected = subprocess.run(["which", "lspci"], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
    if lspci_detected.returncode > 0:
        raise Exception("lspci not detected. Please install pciutils")
    lspci_detected = subprocess.run(["which", "setpci"], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
    if lspci_detected.returncode > 0:
        raise Exception("setpci not detected. Please install pciutils")


def get_device_name(addr):
    p = subprocess.Popen([
        "lspci",
        "-s",
        addr,
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.communicate()[0].splitlines()[0].decode()

def read_all_bytes(device):
    all_bytes = bytearray()
    device_name = get_device_name(device)
    p = subprocess.Popen([
        "lspci",
        "-s",
        device,
        "-xxx"
    ], stdout= subprocess.PIPE, stderr=subprocess.PIPE)
    ret = p.communicate()
    ret = ret[0].decode()
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

def patch_byte(device, position, value):
    subprocess.Popen([
        "setpci",
        "-s",
        device,
        f"{hex(position)}.B={hex(value)}"
    ]).communicate()

def patch_device(addr, aspm_value):
    endpoint_bytes = read_all_bytes(addr)
    byte_position_to_patch = find_byte_to_patch(endpoint_bytes, 0x34)
    if int(endpoint_bytes[byte_position_to_patch]) & 0b11 != aspm_value.value:
        patched_byte = int(endpoint_bytes[byte_position_to_patch])
        patched_byte = patched_byte >> 2
        patched_byte = patched_byte << 2
        patched_byte = patched_byte | aspm_value.value

        patch_byte(addr, byte_position_to_patch, patched_byte)
        print(f"{addr}: Enabled ASPM {aspm_value.name}")
    else:
        print(f"{addr}: Already has ASPM {aspm_value.name} enabled")


def list_supported_devices():
    pcie_addr_regex = r"([0-9a-f]{2}:[0-9a-f]{2}\.[0-9a-f])"
    lspci = subprocess.run("lspci -vv", shell=True, capture_output=True).stdout
    lspci_arr = re.split(pcie_addr_regex, str(lspci))[1:]
    lspci_arr = [ x+y for x,y in zip(lspci_arr[0::2], lspci_arr[1::2]) ]

    aspm_devices = {}
    for dev in lspci_arr:
        device_addr = re.findall(pcie_addr_regex, dev)[0]
        if "ASPM" not in dev or "ASPM not supported" in dev:
            continue
        aspm_support = re.findall(r"ASPM (L[L0-1s ]*),", dev)
        if aspm_support:
            aspm_devices.update({device_addr: ASPM[aspm_support[0].replace(" ", "")]})
    return aspm_devices


def main():
    run_prerequisites()
    for device, aspm_mode in list_supported_devices().items():
        patch_device(device, aspm_mode)

if __name__ == "__main__":
    main()
