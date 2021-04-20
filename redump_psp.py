import argparse
import hashlib
import os
import zlib

from redump_psp_template import TEMPLATE
from sfo_info import get_sfo_info


def hexdump(data, print_offset):
    dump = ""
    for i in range(len(data) // 0x10):
        line = f"{print_offset + i * 16:04x} : "
        for j in range(0x10):
            line += f"{data[i * 16 + j]:02X}"
            line += "  " if j == 0x7 else " "

        r_line = data[i * 0x10 : i * 0x10 + 0x10]
        line += "".join([chr(b) if 0x20 <= b <= 0x7F else "." for b in r_line])

        dump += line + "\n"
    return dump


def gen_hashes(filestream):
    def read_in_chunks(file_object, chunk_size=1024):
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    prev_crc32 = 0
    sha1 = hashlib.sha1()
    md5 = hashlib.md5()
    for piece in read_in_chunks(filestream, 4096):
        prev_crc32 = zlib.crc32(piece, prev_crc32)
        sha1.update(piece)
        md5.update(piece)

    return (format(prev_crc32 & 0xFFFFFFFF, 'x'),
            sha1.hexdigest(),
            md5.hexdigest())

def redump_psp(iso):
    if not os.path.exists(iso):
        print(f"Unable to access {iso}")
        return

    with open(iso, 'rb') as f:
        hashes = gen_hashes(f)
        f.seek(0x800 * 16 + 0x320)  # Go to sector 16 + offset of PVD
        pvd_dump = hexdump(f.read(0x60), 0x320)
    size_b = os.stat(iso).st_size
    size_mb = round(size_b / (1024 * 1024))
    sfo_info = get_sfo_info(iso)

    print(TEMPLATE.format(
        size_mb=size_mb, size_b=size_b,
        md5=hashes[2], sha1=hashes[1], crc32=hashes[0],
        pvd_hexdump=pvd_dump, sfo_info=sfo_info))


parser = argparse.ArgumentParser(
    description='Generate pre-filled redump report from a PSP ISO file')
parser.add_argument('iso', type=str, help='PSP Iso file')
args = parser.parse_args()
redump_psp(args.iso)
