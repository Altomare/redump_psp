from io import BytesIO
import pycdlib
import os
import argparse
import struct
from enum import IntEnum


class DataFormat(IntEnum):
    # Values are read backward
    UTF8_NOTERM = 0x0004
    UTF8 = 0x0204
    INT32 = 0x0404


class SFOHeader:
    def __init__(self, raw):
        # Check magic
        assert(raw[:0x4] == b"\x00PSF")
        self.version = f"{raw[0x04]}.{raw[0x05]}{raw[0x06]}{raw[0x07]}"
        self.key_table_start, self.data_table_start, self.table_entries = \
            struct.unpack('<III', raw[0x08:0x14])


class SFOIndexTable:
    def __init__(self, raw, entries):
        self.entries = []
        for idx in range(entries):
            self.entries.append(SFOIndexTableEntry(raw, 0x14 + idx * 0x10))

    def __getitem__(self, idx):
        return self.entries[idx]

    def __len__(self):
        return len(self.entries)


class SFOIndexTableEntry:
    def __init__(self, raw, offset):
        k_off, d_fmt, d_len, d_max_len, d_offset = \
            struct.unpack('<HHIII', raw[offset: offset + 0x10])

        self.key_offset = k_off
        self.data_fmt = DataFormat(d_fmt)
        self.data_len = d_len
        self.data_max_len = d_max_len
        self.data_offset = d_offset


class SFO:
    def __init__(self, raw_sfo):
        self.header = SFOHeader(raw_sfo)
        self.idx_table = SFOIndexTable(raw_sfo, self.header.table_entries)
        self.dump = ""
        self.dump += f"SFO Version: {self.header.version}\n"

        for i in range(len(self.idx_table)):
            self._read_entry(raw_sfo, i)

    def _read_entry(self, raw_sfo, idx):
        k_start = self.header.key_table_start + self.idx_table[idx].key_offset
        if idx == len(self.idx_table) -1:
            k_end = self.header.data_table_start
        else:
            k_end = self.header.key_table_start + self.idx_table[idx + 1].key_offset
        key = raw_sfo[k_start: k_end].decode('utf8').rstrip("\x00")

        d_start = self.header.data_table_start + self.idx_table[idx].data_offset
        d_end = d_start + self.idx_table[idx].data_len
        if self.idx_table[idx].data_fmt == DataFormat.INT32:
            data = int.from_bytes(raw_sfo[d_start: d_end], "little")
        else:
            data = raw_sfo[d_start: d_end].decode('utf8').rstrip("\x00")

        self.dump += f"{key}: {data}\n"

    def __str__(self):
        return self.dump


def read_iso(path):
    iso = pycdlib.PyCdlib()
    iso.open(path)
    for dirname, dirlist, filelist in iso.walk(iso_path='/'):
        if "PARAM.SFO" in filelist:
            sfo_file = dirname + "/PARAM.SFO"

            extracted = BytesIO()
            iso.get_file_from_iso_fp(extracted, iso_path=sfo_file)
            raw_sfo = extracted.getvalue()

            sfo = SFO(raw_sfo)
            print(f"SFO file: {sfo_file}")
            print(sfo)
    iso.close()


parser = argparse.ArgumentParser(description='Extract SFO info from a PSP ISO')
parser.add_argument('iso', type=str, help='PSP Iso file')
args = parser.parse_args()
read_iso(args.iso)
from io import BytesIO
import pycdlib
import os
import argparse
import struct
from enum import IntEnum


class DataFormat(IntEnum):
    # Values are read backward
    UTF8_NOTERM = 0x0004
    UTF8 = 0x0204
    INT32 = 0x0404


class SFOHeader:
    def __init__(self, raw):
        # Check magic
        assert(raw[:0x4] == b"\x00PSF")
        self.version = f"{raw[0x04]}.{raw[0x05]}{raw[0x06]}{raw[0x07]}"
        self.key_table_start, self.data_table_start, self.table_entries = \
            struct.unpack('<III', raw[0x08:0x14])


class SFOIndexTable:
    def __init__(self, raw, entries):
        self.entries = []
        for idx in range(entries):
            self.entries.append(SFOIndexTableEntry(raw, 0x14 + idx * 0x10))

    def __getitem__(self, idx):
        return self.entries[idx]

    def __len__(self):
        return len(self.entries)


class SFOIndexTableEntry:
    def __init__(self, raw, offset):
        k_off, d_fmt, d_len, d_max_len, d_offset = \
            struct.unpack('<HHIII', raw[offset: offset + 0x10])

        self.key_offset = k_off
        self.data_fmt = DataFormat(d_fmt)
        self.data_len = d_len
        self.data_max_len = d_max_len
        self.data_offset = d_offset


class SFO:
    def __init__(self, raw_sfo):
        self.header = SFOHeader(raw_sfo)
        self.idx_table = SFOIndexTable(raw_sfo, self.header.table_entries)
        self.dump = ""
        self.dump += f"SFO Version: {self.header.version}\n"

        for i in range(len(self.idx_table)):
            self._read_entry(raw_sfo, i)

    def _read_entry(self, raw_sfo, idx):
        k_start = self.header.key_table_start + self.idx_table[idx].key_offset
        if idx == len(self.idx_table) -1:
            k_end = self.header.data_table_start
        else:
            k_end = self.header.key_table_start + self.idx_table[idx + 1].key_offset
        key = raw_sfo[k_start: k_end].decode('utf8').rstrip("\x00")

        d_start = self.header.data_table_start + self.idx_table[idx].data_offset
        d_end = d_start + self.idx_table[idx].data_len
        if self.idx_table[idx].data_fmt == DataFormat.INT32:
            data = int.from_bytes(raw_sfo[d_start: d_end], "little")
        else:
            data = raw_sfo[d_start: d_end].decode('utf8').rstrip("\x00")

        self.dump += f"{key}: {data}\n"

    def __str__(self):
        return self.dump


def read_iso(path):
    iso = pycdlib.PyCdlib()
    iso.open(path)
    for dirname, dirlist, filelist in iso.walk(iso_path='/'):
        if "PARAM.SFO" in filelist:
            sfo_file = dirname + "/PARAM.SFO"

            extracted = BytesIO()
            iso.get_file_from_iso_fp(extracted, iso_path=sfo_file)
            raw_sfo = extracted.getvalue()

            sfo = SFO(raw_sfo)
            print(f"SFO file: {sfo_file}")
            print(sfo)
    iso.close()


parser = argparse.ArgumentParser(description='Extract SFO info from a PSP ISO')
parser.add_argument('iso', type=str, help='PSP Iso file')
args = parser.parse_args()
read_iso(args.iso)
