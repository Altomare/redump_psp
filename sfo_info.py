from io import BytesIO
import pycdlib
import os
import argparse
from enum import Enum, auto


def to_int(data, offset, length):
    return int.from_bytes(data[offset: offset + length], "little")


class DataFormat(Enum):
    UTF8_NOTERM = auto()
    UTF8 = auto()
    INT32 = auto()


class SFOHeader:
    def __init__(self, raw):
        # Check magic
        assert(raw[:0x4] == b"\x00PSF")
        version_major = int(raw[0x04])
        version_minor = int(raw[0x05])
        self.version = f"{version_major}.{version_minor}"
        self.key_table_start = to_int(raw, 0x08, 0x04)
        self.data_table_start = to_int(raw, 0x0C, 0x04)
        self.table_entries = to_int(raw, 0x10, 0x04)


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
        self.key_offset = to_int(raw, offset, 0x02)
        fmt = raw[offset + 0x02: offset + 0x04]
        if fmt == b"\x04\x00":
            self.data_fmt = DataFormat.UTF8_NOTERM
        elif fmt == b"\x04\x02":
            self.data_fmt = DataFormat.UTF8
        elif fmt == b"\x04\x04":
            self.data_fmt = DataFormat.INT32
        else:
            raise ValueError(f"Unknown data format: 0x{fmt.hex()}")
        self.data_len = to_int(raw, offset + 0x04, 0x04)
        self.data_max_len = to_int(raw, offset + 0x08, 0x04)
        self.data_offset = to_int(raw, offset + 0x0C, 0x04)


class SFO:
    def __init__(self, raw_sfo):
        self.header = SFOHeader(raw_sfo)
        self.idx_table = SFOIndexTable(raw_sfo, self.header.table_entries)
        self.dump = ""
        self.dump += f"SFO Version: {self.header.version}\n"

        for i in range(len(self.idx_table)):
            self._read_entry(raw_sfo, i)

    def _read_entry(self, raw_sfo, idx):
        key_offset = self.header.key_table_start + self.idx_table[idx].key_offset
        if idx == len(self.idx_table) -1:
            key_end_offset = self.header.data_table_start
        else:
            key_end_offset = self.header.key_table_start + self.idx_table[idx + 1].key_offset
        key = raw_sfo[key_offset: key_end_offset].decode('utf8').rstrip("\x00")

        data_offset = self.header.data_table_start + self.idx_table[idx].data_offset
        data_end_offset = self.header.data_table_start + self.idx_table[idx].data_offset + self.idx_table[idx].data_len
        if self.idx_table[idx].data_fmt == DataFormat.INT32:
            data = int.from_bytes(raw_sfo[data_offset: data_end_offset], "little")
        else:
            data = raw_sfo[data_offset: data_end_offset].decode('utf8').rstrip("\x00")

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
