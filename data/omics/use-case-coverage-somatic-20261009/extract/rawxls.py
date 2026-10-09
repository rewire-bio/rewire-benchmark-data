"""Read legacy BIFF8 .xls cells as stored values, with the standard library only.

Numbers are returned as the shortest repr of the stored IEEE double (or the decoded RK value);
strings come from the shared string table. No number formatting is applied."""
import struct

FREE, END = 0xFFFFFFFF, 0xFFFFFFFE


def ole_stream(data, want):
    if data[:8] != bytes.fromhex('D0CF11E0A1B11AE1'):
        raise ValueError('not an OLE2 compound file')
    ssz = 1 << struct.unpack_from('<H', data, 30)[0]
    mssz = 1 << struct.unpack_from('<H', data, 32)[0]
    nfat, dir_start = struct.unpack_from('<II', data, 44)
    cutoff, mini_start, nmini, difat_start, ndifat = struct.unpack_from('<IIIII', data, 56)
    sec = lambda i: data[512 + i * ssz: 512 + (i + 1) * ssz]
    difat = list(struct.unpack_from('<109I', data, 76))
    d = difat_start
    for _ in range(ndifat):
        block = sec(d)
        difat += struct.unpack_from('<%dI' % (ssz // 4 - 1), block)
        d = struct.unpack_from('<I', block, ssz - 4)[0]
    fat = []
    for s in difat[:nfat]:
        fat += struct.unpack('<%dI' % (ssz // 4), sec(s))
    def chain(start, table):
        out, i, seen = [], start, set()
        while i not in (END, FREE) and i < len(table):
            if i in seen:
                raise ValueError('cyclic sector chain')
            seen.add(i); out.append(i); i = table[i]
        return out
    directory = b''.join(sec(i) for i in chain(dir_start, fat))
    entries = []
    for k in range(len(directory) // 128):
        e = directory[k * 128:(k + 1) * 128]
        nlen = struct.unpack_from('<H', e, 64)[0]
        name = e[:max(nlen - 2, 0)].decode('utf-16-le')
        start, size = struct.unpack_from('<II', e, 116)
        entries.append((name, e[66], start, size))
    root = entries[0]
    for name, typ, start, size in entries:
        if name != want:
            continue
        if size >= cutoff:
            return b''.join(sec(i) for i in chain(start, fat))[:size]
        minifat = []
        for s in chain(mini_start, fat):
            minifat += struct.unpack('<%dI' % (ssz // 4), sec(s))
        ministream = b''.join(sec(i) for i in chain(root[2], fat))
        return b''.join(ministream[i * mssz:(i + 1) * mssz] for i in chain(start, minifat))[:size]
    raise KeyError(want)


def records(stream):
    pos = 0
    while pos + 4 <= len(stream):
        rtype, rlen = struct.unpack_from('<HH', stream, pos)
        yield pos, rtype, stream[pos + 4:pos + 4 + rlen]
        pos += 4 + rlen


def rk(v):
    if v & 2:
        x = v >> 2
        if x & (1 << 29):
            x -= 1 << 30
        val = float(x)
    else:
        val = struct.unpack('<d', struct.pack('<Q', (v & 0xFFFFFFFC) << 32))[0]
    if v & 1:
        val /= 100
    return val


def num(x):
    if x == int(x) and abs(x) < 1e15:
        return str(int(x))
    return repr(x)


def parse_sst(chunks):
    """chunks: SST payload followed by CONTINUE payloads."""
    total, unique = struct.unpack_from('<II', chunks[0], 0)
    ci, pos = 0, 8
    out = []
    def need(n):
        nonlocal ci, pos
        if pos + n > len(chunks[ci]):
            if pos != len(chunks[ci]):
                raise ValueError('SST field split across CONTINUE')
            ci += 1; pos = 0
    for _ in range(unique):
        need(3)
        cch, flags = struct.unpack_from('<HB', chunks[ci], pos); pos += 3
        rich = struct.unpack_from('<H', chunks[ci], pos)[0] if flags & 8 else 0
        pos += 2 if flags & 8 else 0
        ext = struct.unpack_from('<I', chunks[ci], pos)[0] if flags & 4 else 0
        pos += 4 if flags & 4 else 0
        wide = flags & 1
        chars, left = [], cch
        while left:
            if pos >= len(chunks[ci]):
                ci += 1; pos = 0
                wide = chunks[ci][0] & 1; pos = 1
            avail = (len(chunks[ci]) - pos) // (2 if wide else 1)
            take = min(left, avail)
            raw = chunks[ci][pos:pos + take * (2 if wide else 1)]
            chars.append(raw.decode('utf-16-le' if wide else 'latin-1'))
            pos += len(raw); left -= take
        skip = rich * 4 + ext
        while skip:
            if pos >= len(chunks[ci]):
                ci += 1; pos = 0
            take = min(skip, len(chunks[ci]) - pos); pos += take; skip -= take
        out.append(''.join(chars))
    return out


def col_name(c):
    s = ''
    c += 1
    while c:
        c, r = divmod(c - 1, 26); s = chr(65 + r) + s
    return s


def read(path):
    data = open(path, 'rb').read()
    wb = ole_stream(data, 'Workbook')
    sheets, sst = [], []
    recs = list(records(wb))
    for k, (pos, rtype, body) in enumerate(recs):
        if rtype == 0x85:
            off, vis, typ, cch, flags = struct.unpack_from('<IBBBB', body, 0)
            name = body[8:8 + cch * (2 if flags & 1 else 1)].decode('utf-16-le' if flags & 1 else 'latin-1')
            sheets.append((name, off))
        elif rtype == 0xFC:
            chunks = [body]
            j = k + 1
            while j < len(recs) and recs[j][1] == 0x3C:
                chunks.append(recs[j][2]); j += 1
            sst = parse_sst(chunks)
    out = {}
    for name, off in sheets:
        cells = {}
        pending = None
        for pos, rtype, body in records(wb[off:]):
            if rtype == 0x0A:  # EOF
                break
            if rtype in (0xFD, 0x203, 0x27E, 0x204, 0x06, 0x205):
                r, c = struct.unpack_from('<HH', body, 0)
                ref = col_name(c) + str(r + 1)
            if rtype == 0xFD:
                cells[ref] = sst[struct.unpack_from('<I', body, 6)[0]]
            elif rtype == 0x203:
                cells[ref] = num(struct.unpack_from('<d', body, 6)[0])
            elif rtype == 0x27E:
                cells[ref] = num(rk(struct.unpack_from('<I', body, 6)[0]))
            elif rtype == 0xBD:
                r, c0 = struct.unpack_from('<HH', body, 0)
                n = (len(body) - 6) // 6
                for i in range(n):
                    v = struct.unpack_from('<I', body, 4 + i * 6 + 2)[0]
                    cells[col_name(c0 + i) + str(r + 1)] = num(rk(v))
            elif rtype == 0x204:
                cch, flags = struct.unpack_from('<HB', body, 6)
                cells[ref] = body[9:9 + cch * (2 if flags & 1 else 1)].decode('utf-16-le' if flags & 1 else 'latin-1')
            elif rtype == 0x06:
                res = body[6:14]
                if res[6:8] == b'\xff\xff':
                    if res[0] == 0:
                        pending = ref
                    elif res[0] == 1:
                        cells[ref] = 'TRUE' if res[2] else 'FALSE'
                    elif res[0] == 2:
                        cells[ref] = '#ERR%d' % res[2]
                    else:
                        cells[ref] = ''
                else:
                    cells[ref] = num(struct.unpack('<d', res)[0])
            elif rtype == 0x207 and pending:
                cch, flags = struct.unpack_from('<HB', body, 0)
                cells[pending] = body[3:3 + cch * (2 if flags & 1 else 1)].decode('utf-16-le' if flags & 1 else 'latin-1')
                pending = None
            elif rtype == 0x205:
                v, iserr = body[6], body[7]
                cells[ref] = ('#ERR%d' % v) if iserr else ('TRUE' if v else 'FALSE')
        out[name] = cells
    return out


if __name__ == '__main__':
    import sys
    for name, cells in read(sys.argv[1]).items():
        print('==', name, len(cells))
