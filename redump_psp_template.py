
TEMPLATE = """\
General Info:
[code]
Game Name:    <FILL_ME>
Serial Number:<FILL_ME>
Dumping PSP:  <FILL_ME>
Dumping Tool: <FILL_ME>
Filesize:     {size_mb:,} MB ({size_b:,} bytes)
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
MD5:   {md5}
SHA1:  {sha1}
CRC32: {crc32}
SHA256: {sha256}
[/code]

Primary Volume Descriptor (PVD)
[code]
{pvd_hexdump}
[/code]

SFO Info:
[code]
{sfo_info}
[/code]
"""
