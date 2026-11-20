"""Leitura de metricas reais da fonte (WOFF) sem dependencias externas.

Usado para medir cada linha de texto antes de posicionar no slide, de modo que
nenhum bloco de texto ultrapasse sua area.
"""
import struct
import zlib


def _tables(path):
    data = open(path, "rb").read()
    num_tables = struct.unpack(">H", data[12:14])[0]
    off = 44
    tabs = {}
    for _ in range(num_tables):
        tag, offset, comp_len, orig_len, _cs = struct.unpack(">4sIIII", data[off:off + 20])
        off += 20
        tabs[tag.decode()] = (offset, comp_len, orig_len)
    return data, tabs


def _table(data, tabs, tag):
    off, comp_len, orig_len = tabs[tag]
    raw = data[off:off + comp_len]
    return zlib.decompress(raw) if comp_len < orig_len else raw


class Font:
    def __init__(self, path):
        data, tabs = _tables(path)
        head = _table(data, tabs, "head")
        hhea = _table(data, tabs, "hhea")
        hmtx = _table(data, tabs, "hmtx")
        cmap = _table(data, tabs, "cmap")
        self.upem = struct.unpack(">H", head[18:20])[0]
        n_hmetrics = struct.unpack(">H", hhea[34:36])[0]
        self.advances = [
            struct.unpack(">H", hmtx[i * 4:i * 4 + 2])[0] for i in range(n_hmetrics)
        ]
        self.cmap = self._parse_cmap(cmap)

    @staticmethod
    def _parse_cmap(cmap):
        n = struct.unpack(">H", cmap[2:4])[0]
        sub = None
        for i in range(n):
            pid, eid, off = struct.unpack(">HHI", cmap[4 + i * 8:12 + i * 8])
            if struct.unpack(">H", cmap[off:off + 2])[0] == 4:
                sub = off
                break
        assert sub is not None, "cmap formato 4 nao encontrado"
        seg_x2 = struct.unpack(">H", cmap[sub + 6:sub + 8])[0]
        segs = seg_x2 // 2
        base = sub + 14
        end = [struct.unpack(">H", cmap[base + 2 * i:base + 2 * i + 2])[0] for i in range(segs)]
        start_base = base + seg_x2 + 2
        start = [struct.unpack(">H", cmap[start_base + 2 * i:start_base + 2 * i + 2])[0] for i in range(segs)]
        delta_base = start_base + seg_x2
        delta = [struct.unpack(">h", cmap[delta_base + 2 * i:delta_base + 2 * i + 2])[0] for i in range(segs)]
        ro_base = delta_base + seg_x2
        range_offset = [struct.unpack(">H", cmap[ro_base + 2 * i:ro_base + 2 * i + 2])[0] for i in range(segs)]
        mapping = {}
        for i in range(segs):
            for c in range(start[i], min(end[i], 0xFFFF) + 1):
                if range_offset[i] == 0:
                    g = (c + delta[i]) & 0xFFFF
                else:
                    gi = ro_base + 2 * i + range_offset[i] + 2 * (c - start[i])
                    g = struct.unpack(">H", cmap[gi:gi + 2])[0]
                    if g:
                        g = (g + delta[i]) & 0xFFFF
                mapping[chr(c)] = g
        return mapping

    def width_em(self, text):
        total = 0
        for ch in text:
            g = self.cmap.get(ch)
            if g is None:
                g = self.cmap.get("?")
            idx = g if g < len(self.advances) else len(self.advances) - 1
            total += self.advances[idx]
        return total / self.upem
