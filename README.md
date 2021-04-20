# PSP ISO Tools for Redump

This repository contains portable Python replacements for the tools required by Redump when submitting PSP games.
IsoBuster, Hashcalc and SFOInfo are replaced by the `redump_psp.py` script.

Given an ISO file, it will generate a pre-filled Redump submission, containing:
- File size
- Hashes (MD5, CRC32, SHA1)
- ISO PVD Hexdump
- SFO information

`sfo_info.py` can be used by itself as a standalone sfo_info.exe replacement that works on Linux too.



# Requirements

- Python 3.4 or superior
- pycdlib
