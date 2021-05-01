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

- Python 3 (>= 3.4)
- pycdlib

Windows exe builds are available in the release tab.


# Usage

`redump_psp <iso_file> [--out <output_file>]`

`sfo_info <iso_file>`


# Sample output

It is formatted for Redump forum posts, hence the \[code] tags. You can easily remove them in `redump_psp_template.py` if needed.

```
General Info:
[code]
Game Name:    <FILL_ME>
Serial Number:<FILL_ME>
Dumping PSP:  <FILL_ME>
Dumping Tool: <FILL_ME>
Filesize:     1,495 MB (1,568,079,872 bytes)
Barcode:      <FILL_ME>
Edition:      <FILL_ME>
Languages:    <FILL_ME>
Ring Codes:
- Outer Ring Mastering Code (laser branded/etched): <FILL_ME>
- Outer Ring Mastering SID Code: <FILL_ME>
- Outer Ring Toolstamp (engraved/stamped): <FILL_ME>
- Inner Ring Mastering Code (laser branded/etched): <FILL_ME>
- Inner Ring Mastering SID Code: <FILL_ME>
- Inner Ring Toolstamp (engraved/stamped): <FILL_ME>
- Mould SID Code: <FILL_ME>
[/code]

HashCalc Info:
[code]
MD5:   dd60041bfb6d677fdaacd2cf9cb6d84a
SHA1:  88a19042041ff368b9cb887432cb5255c654c33c
CRC32: 83adb164
[/code]

Primary Volume Descriptor (PVD)
[code]
0320 : 20 20 20 20 20 20 20 20  20 20 20 20 20 32 30 30                200
0330 : 35 30 34 32 31 31 35 33  33 31 38 30 30 24 30 30   5042115331800$00
0340 : 30 30 30 30 30 30 30 30  30 30 30 30 30 30 00 30   00000000000000.0
0350 : 30 30 30 30 30 30 30 30  30 30 30 30 30 30 30 00   000000000000000.
0360 : 30 30 30 30 30 30 30 30  30 30 30 30 30 30 30 30   0000000000000000
0370 : 00 02 00 55 43 45 54 2D  30 30 30 30 36 7C 45 32   ...UCET-00006|E2
[/code]

SFO Info:
[code]
SFO file: /PSP_GAME/PARAM.SFO
SFO Version: 1.1
BOOTABLE: 1
CATEGORY: UG
DISC_ID: UCET00006
DISC_NUMBER: 1
DISC_TOTAL: 1
DISC_VERSION: 0.01
PARENTAL_LEVEL: 2
PSP_SYSTEM_VER: 1.50
REGION: 32768
TITLE: WRC

SFO file: /PSP_GAME/SYSDIR/UPDATE/PARAM.SFO
SFO Version: 1.1
BOOTABLE: 1
CATEGORY: MG
DISC_VERSION: 1.00
PARENTAL_LEVEL: 1
REGION: 32768
TITLE: PSP™ Update ver 1.50
TITLE_0: PSP™ アップデート ver 1.50
TITLE_2: Mise à jour PSP™ ver. 1.50
TITLE_3: Actualización de PSP™ ver. 1.50
TITLE_4: PSP™-Aktualisierung Ver. 1.50
TITLE_5: Aggiornamento della PSP™
ver. 1.50
TITLE_6: PSP™-update versie 1.50
TITLE_7: Actualização PSP™ ver 1.50
TITLE_8: Обновление PSP™ вер. 1.50
UPDATER_VER: 1.50
[/code]
```

# Using it in other scripts

Since this is just scripts and was not made like a module, some modifications are needed if you want to import the Python code in some bigger project.
The easiest (and quite ugly) solution is to add a `__init__.py` file, containing:
```Python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".", "."))
```
This adds the whole directory to the path, so beware.

Below is a simple script I've made that auto-generates submissions for every ISO in the given directory.
Make sure it only contains PSP ISOs.
```Python
import os
from redump_psp.redump_psp import gen_psp_redump
import argparse

parser = argparse.ArgumentParser(
    description='Find ISOs and generate redump submissions')
parser.add_argument('dir', type=str, help='Directory')
args = parser.parse_args()

for root, dirs, files in os.walk(args.dir):
    for name in files:
        if not name.endswith('.iso'):
            continue

        iso_name = name[:-4]
        if iso_name + '.nfo' in files:
            continue

        gen_psp_redump(os.path.join(root, iso_name + '.iso'),
                       os.path.join(root, iso_name + '.nfo'))
        print(f"Generated submission for {name}")
```
