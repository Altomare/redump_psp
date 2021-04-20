from io import BytesIO
import pycdlib
import os
import argparse
import struct
from enum import IntEnum


class SFODataFormat(IntEnum):
    # Values are read backward
    UTF8_NOTERM = 0x0004
    UTF8 = 0x0204
    INT32 = 0x0404


class SFOHeader:
    def __init__(self, raw):
        # Check magic
        assert(raw[:0x4] == b"\x00PSF")
        version_minor = struct.unpack("<I", raw[0x5:0x8] + b"\x00")[0]
        self.version = f"{raw[0x04]}.{version_minor}"
        self.key_table_start, self.data_table_start, self.table_entries = \
            struct.unpack('<III', raw[0x08:0x14])


class SFOIndexTableEntry:
    def __init__(self, raw, offset):
        fields = struct.unpack('<HHIII', raw[offset: offset + 0x10])
        self.key_offset = fields[0]
        self.data_fmt = SFODataFormat(fields[1])
        self.data_len = fields[2]
        self.data_max_len = fields[3]
        self.data_offset = fields[4]


class SFO:
    def __init__(self, raw_sfo):
        self.header = SFOHeader(raw_sfo)

        self.idx_table = []
        for idx in range(self.header.table_entries):
            self.idx_table.append(SFOIndexTableEntry(raw_sfo, 0x14 + idx * 0x10))

        self.data = {}
        for i in range(len(self.idx_table)):
            self._read_entry(raw_sfo, i)

    def _read_entry(self, raw_sfo, idx):
        key_table_start = self.header.key_table_start
        data_table_start = self.header.data_table_start
        entry = self.idx_table[idx]

        # Read key from key table
        k_start = key_table_start + entry.key_offset
        if idx == len(self.idx_table) - 1:
            k_end = data_table_start
        else:
            k_end = key_table_start + self.idx_table[idx + 1].key_offset
        key = raw_sfo[k_start: k_end].decode('utf8').rstrip("\x00")

        # Read data from data table
        d_start = data_table_start + entry.data_offset
        d_end = d_start + entry.data_len
        if entry.data_fmt == SFODataFormat.INT32:
            data = int.from_bytes(raw_sfo[d_start: d_end], "little")
        else:
            data = raw_sfo[d_start: d_end].decode('utf8').rstrip("\x00")

        self.data[key] = data

    def dump(self):
        dump = ""
        dump += f"SFO Version: {self.header.version}\n"
        for key in self.data.keys():
            dump += f"{key}: {self.data[key]}\n"
        return dump


def get_sfo_info(path):
    iso = pycdlib.PyCdlib()
    iso.open(path)
    out = ""
    for dirname, dirlist, filelist in iso.walk(iso_path='/'):
        for file in filelist:
            if not file.endswith('.SFO'):
                continue
            sfo_file = dirname + "/" + file

            extracted = BytesIO()
            iso.get_file_from_iso_fp(extracted, iso_path=sfo_file)
            raw_sfo = extracted.getvalue()

            sfo = SFO(raw_sfo)
            out += f"SFO file: {sfo_file}\n"
            out += sfo.dump() + "\n"
    iso.close()
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract SFO info from a PSP ISO')
    parser.add_argument('iso', type=str, help='PSP Iso file')
    args = parser.parse_args()
    print(get_sfo_info(args.iso))


# Argument, take iso
# Get hash
# Get PVD
# Get SFO Info
# Print template
