"""Converte WOFF (sfnt comprimido por tabela) em TTF para render de preview."""
import struct
import sys


def woff_to_ttf(src, dst):
    data = open(src, "rb").read()
    assert data[:4] == b"wOFF"
    _sig, flavor, _length, num_tables = struct.unpack(">4sIIH", data[:14])
    off = 44
    entries = []
    for _ in range(num_tables):
        tag, offset, comp_len, orig_len, checksum = struct.unpack(">4sIIII", data[off:off + 20])
        off += 20
        raw = data[offset:offset + comp_len]
        if comp_len < orig_len:
            import zlib
            raw = zlib.decompress(raw)
        entries.append([tag, raw, checksum])

    def checksum(buf):
        buf = buf + b"\0" * ((4 - len(buf) % 4) % 4)
        return sum(struct.unpack(">%dI" % (len(buf) // 4), buf)) & 0xFFFFFFFF

    entries.sort(key=lambda e: e[0])
    n = len(entries)
    search_range = 16 * (2 ** (n.bit_length() - 1))
    header = struct.pack(">IHHHH", flavor, n, search_range, n.bit_length() - 1, n * 16 - search_range)
    directory = b""
    cursor = 12 + 16 * n
    payload = b""
    for tag, raw, _cs in entries:
        directory += struct.pack(">4sIII", tag, checksum(raw), cursor + len(payload), len(raw))
        pad = (4 - len(raw) % 4) % 4
        payload += raw + b"\0" * pad
    open(dst, "wb").write(header + directory + payload)


if __name__ == "__main__":
    for weight in ("400", "500", "700"):
        woff_to_ttf("fonts/roboto-latin-%s-normal.woff" % weight,
                    "fonts/Roboto-%s.ttf" % weight)
    print("ok")
