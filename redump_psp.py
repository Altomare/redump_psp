import argparse
import hashlib
import os
import sys
import zlib

from redump_psp_template import TEMPLATE
from sfo_info import get_sfo_info


def hexdump(data, offset, size):
    """Return hexdump string of given data in isobuster format."""
    def ascii_print(c):
        return chr(c) if 32 <= c <= 127 else "."

    dump = ""
    for i in range(size // 0x10):
        line_offset = offset + i * 0x10
        line_data = data[line_offset: line_offset + 0x10]

        line_format = "{:04X} :" + " {:02X}" * 8 + " " + " {:02X}" * 8
        dump += line_format.format(line_offset, *line_data)
        dump += "   " + "".join([ascii_print(b) for b in line_data]) + "\n"
    return dump


def gen_hashes(filestream):
    def read_in_chunks(file_object, chunk_size):
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    filestream.seek(0)
    prev_crc32 = 0
    sha1 = hashlib.sha1()
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    for piece in read_in_chunks(filestream, 0x10000):
        prev_crc32 = zlib.crc32(piece, prev_crc32)
        sha1.update(piece)
        md5.update(piece)
        sha256.update(piece)

    return (format(prev_crc32 & 0xFFFFFFFF, 'x').zfill(8),
            sha1.hexdigest().zfill(40),
            md5.hexdigest().zfill(32),
            sha256.hexdigest().zfill(64))


def get_pvd_dump(filestream):
    # Locate PVD sector, starting from sector 0x10
    # See: https://wiki.osdev.org/ISO_9660#Volume_Descriptors
    filestream.seek(0x8000)
    raw_sector = filestream.read(0x800)
    while raw_sector[0] != 0xFF:
        if raw_sector[0] == 0x01:
            return hexdump(raw_sector, 0x320, 0x60)
        raw_sector = filestream.read(0x800)
    raise Exception("Could not find PVD")


def gen_psp_redump(iso, out):
    if not os.path.exists(iso):
        print(f"Unable to access {iso}")
        return

    with open(iso, 'rb') as f:
        hashes = gen_hashes(f)
        pvd_dump = get_pvd_dump(f)
    size_b = os.stat(iso).st_size
    size_mb = round(size_b / (1024 * 1024))
    sfo_info = get_sfo_info(iso)

    dump = TEMPLATE.format(
        size_mb=size_mb, size_b=size_b,
        md5=hashes[2], sha1=hashes[1], crc32=hashes[0], sha256=hashes[3],
        pvd_hexdump=pvd_dump.strip('\n'), sfo_info=sfo_info)
    if out:
        with open(out, 'w', encoding='utf8') as f:
            f.write(dump)
    else:
        print(dump)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate pre-filled redump report from a PSP ISO file')
    parser.add_argument('iso', type=str, help='PSP Iso file')
    parser.add_argument('--out', dest='out_file', default=None,
                        help='output file')
    args = parser.parse_args()
    if args.out_file and os.path.exists(args.out_file):
        print("Output file already exists, aborting.")
        sys.exit(1)
    gen_psp_redump(args.iso, args.out_file)
