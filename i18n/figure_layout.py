"""Layout the current published SVG nodes without running a model/generator.

The horizontal coordinate system is immutable: matrix cells, axes and
proportional bars retain their original x values. English is wrapped at word
boundaries at the original font size. Extra line height is inserted into a
monotone vertical map; boxes, lanes, paths and arrow endpoints consume that
same map. This preserves the published frame's actual colors and identity.

Measurement reads the installed Arial advance tables using only the stdlib.
The conservative portable fallback does not require a font package.
"""
from __future__ import annotations

from dataclasses import dataclass
import bisect
import copy
import html
import math
import re
import unicodedata
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG_NS)
CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff]')
NUMBER = re.compile(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?')
TOKEN_ONLY = re.compile(r'^(?:(?:我|爱|学习|你|！)|[\s·/／、，,\[\]→+]|PAD|BOS|EOS)+$')
GEOMETRY_TAGS = frozenset(('rect', 'line', 'path', 'polygon', 'polyline', 'circle', 'ellipse', 'g'))
Y_ATTRIBUTES = frozenset(('y', 'y1', 'y2', 'cy', 'height', 'd', 'points'))


class LayoutError(ValueError):
    pass


def tag(element):
    return element.tag.rsplit('}', 1)[-1]


def num(value, default=0.0):
    try:
        return float(value) if value is not None else float(default)
    except (TypeError, ValueError) as error:
        raise LayoutError('non-numeric SVG coordinate: %r' % value) from error


def fmt(value):
    return ('%.4f' % value).rstrip('0').rstrip('.') or '0'


def parse(source):
    try:
        node = ET.fromstring(source)
    except ET.ParseError as error:
        raise LayoutError('invalid published SVG: %s' % error) from error
    if tag(node) != 'svg':
        raise LayoutError('expected one SVG root')
    if any(tag(e) in ('script', 'foreignObject', 'image', 'use') for e in node.iter()):
        raise LayoutError('unsupported external/executable SVG element')
    if any(e.get('transform') for e in node.iter()):
        raise LayoutError('transformed SVG requires an explicit layout owner')
    return node


def translatable(value):
    return bool(CJK.search(value)) and not TOKEN_ONLY.fullmatch(value.strip())


def content(element):
    return ''.join(element.itertext())


def _style(element):
    return tuple((k, v) for k, v in element.attrib.items()
                 if k not in ('x', 'y', 'id', 'aria-label', 'aria-labelledby'))


@dataclass
class TextGroup:
    nodes: list
    source: str
    x: float
    y: float
    size: float
    anchor: str
    source_parts: tuple = ()


def text_groups(root):
    """Recover adjacent wrapped lines, never combine distinct table cells.

    Published generators emit one sibling text node per wrapped line. The
    same x/font/anchor and their 1.3..1.6 em line step identify that local
    paragraph. Shapes, different styles and column changes are hard bounds.
    """
    groups = []
    for parent in root.iter():
        children = list(parent)
        index = 0
        while index < len(children):
            node = children[index]
            if tag(node) != 'text':
                index += 1
                continue
            values = [node]
            x, y = num(node.get('x')), num(node.get('y'))
            size = num(node.get('font-size'), 16)
            # Existing tspans are one semantic text block (AP tables).
            if not list(node):
                while index + 1 < len(children):
                    other = children[index + 1]
                    if tag(other) != 'text' or list(other):
                        break
                    dy = num(other.get('y')) - num(values[-1].get('y'))
                    if (abs(num(other.get('x')) - x) > .01 or
                            _style(other) != _style(node) or
                            not 1.28 * size <= dy <= 1.62 * size or
                            other.get('id') or values[-1].get('id')):
                        break
                    # Pure numeric rows and separate token labels are data.
                    joined = ''.join(content(e) for e in values) + content(other)
                    if not CJK.search(joined) or TOKEN_ONLY.fullmatch(joined.strip()):
                        break
                    values.append(other)
                    index += 1
            groups.append(TextGroup(values, ''.join(content(e) for e in values),
                                    x, y, size, node.get('text-anchor', 'start')))
            index += 1
    return groups


def rendering_groups(root, groups):
    """Join issued short-leading fragments without changing translation keys.

    The visual para primitive also uses 19px leading at 16px. Those fragments
    already have permanent table IDs, so inventory keeps them separate while
    rendering consumes their translated pieces as one logical paragraph.
    """
    positions = {child: (parent, index) for parent in root.iter()
                 for index, child in enumerate(parent)}
    result = []
    for group in groups:
        previous = result[-1] if result else None
        if previous is not None:
            parent, index = positions[group.nodes[0]]
            old_parent, old_index = positions[previous.nodes[-1]]
            gap = group.y - num(previous.nodes[-1].get('y'))
            if (parent is old_parent and index == old_index + 1 and
                    abs(group.x - previous.x) < .01 and
                    _style(group.nodes[0]) == _style(previous.nodes[0]) and
                    1.05 * group.size <= gap < 1.28 * group.size and
                    translatable(previous.source) and translatable(group.source) and
                    not any(n.get('id') for n in previous.nodes + group.nodes)):
                parts = previous.source_parts or (previous.source,)
                previous.nodes.extend(group.nodes)
                previous.source_parts = parts + (group.source,)
                previous.source += group.source
                continue
        result.append(group)
    return result


def strings(root, include_text=True):
    """Return source text with source boundary whitespace intact."""
    out = []
    for element in root.iter():
        if tag(element) in ('title', 'desc') and translatable(content(element)):
            out.append(('accessibility', content(element)))
        for attribute in ('aria-label',):
            value = element.get(attribute, '')
            if translatable(value):
                out.append(('attribute', value))
    if include_text:
        out.extend(('text', g.source) for g in text_groups(root) if translatable(g.source))
    return out


_FONTS = {}


class FontMetrics:
    """Read cmap/hmtx from the installed Arial face using only the stdlib."""
    def __init__(self, path):
        self.data = Path(path).read_bytes()
        u16 = lambda offset: struct.unpack_from('>H', self.data, offset)[0]
        u32 = lambda offset: struct.unpack_from('>I', self.data, offset)[0]
        tables = {}
        for i in range(u16(4)):
            offset = 12 + i * 16
            name = self.data[offset:offset+4].decode('ascii')
            tables[name] = u32(offset + 8)
        self.units = u16(tables['head'] + 18)
        number = u16(tables['hhea'] + 34)
        self.advances = [u16(tables['hmtx'] + i * 4) for i in range(number)]
        cmap = tables['cmap'];chosen = None
        for i in range(u16(cmap + 2)):
            record = cmap + 4 + i * 8
            offset = cmap + u32(record + 4)
            kind = u16(offset)
            if kind in (4, 12) and (chosen is None or kind > chosen[0]):
                chosen = (kind, offset)
        self.mapping = {}
        if chosen is None:
            raise LayoutError('Arial font has no usable Unicode cmap')
        kind, offset = chosen
        if kind == 12:
            for i in range(u32(offset + 12)):
                start, end, glyph = struct.unpack_from('>III', self.data, offset + 16 + i * 12)
                for code in range(start, min(end, 0xFFFF) + 1):
                    self.mapping[code] = glyph + code - start
        else:
            n = u16(offset + 6) // 2
            ends = offset + 14;starts = ends + 2 * n + 2
            deltas = starts + 2 * n;ranges = deltas + 2 * n
            for i in range(n):
                start, end, delta, distance = u16(starts+i*2), u16(ends+i*2), u16(deltas+i*2), u16(ranges+i*2)
                for code in range(start, end+1):
                    if distance:
                        glyph = u16(ranges + i*2 + distance + (code-start)*2)
                        if glyph:
                            glyph = (glyph + delta) & 0xFFFF
                    else:
                        glyph = (code + delta) & 0xFFFF
                    self.mapping[code] = glyph

    def width(self, value, size):
        total = 0
        for char in value:
            glyph = self.mapping.get(ord(char))
            if glyph is None:
                total += self.units if unicodedata.east_asian_width(char) in 'WF' else self.units * .9
            else:
                total += self.advances[min(glyph, len(self.advances)-1)]
        return total * size / self.units * 1.025


def width(value, size=16, bold=False):
    """Arial advance metrics with 2.5% padding; missing glyphs use a safe em."""
    name = '/System/Library/Fonts/Supplemental/Arial%s.ttf' % (' Bold' if bold else '')
    if name not in _FONTS:
        _FONTS[name] = FontMetrics(name) if Path(name).is_file() else None
    font = _FONTS[name]
    if font is not None:
        return font.width(str(value), size)
    return sum(size * (1.05 if unicodedata.east_asian_width(c) in 'WF'
                       or c in 'MW@%&' else .7 if c.isupper()
                       else .34 if c in "ilI.,:;!|'` " else .62)
               for c in str(value)) * (1.04 if bold else 1)


def wrap(value, limit, size=16, bold=False):
    """Wrap at whitespace; a long code/URL gets its own measured-width line.

    A technical identifier is never sliced into fragments. Its required width
    is returned to the slot planner, which may use the remaining full row.
    """
    if limit < size:
        raise LayoutError('text slot narrower than one readable glyph')
    result = []
    for paragraph in str(value).split('\n'):
        words = re.findall(r'\S+', paragraph)
        line = ''
        for original_word in words:
            # Existing prose hyphens/slashes are legal break opportunities.
            # Identifiers containing underscores/digits remain indivisible.
            pieces = re.split(r'(?<=[-/])(?=[A-Za-z])', original_word) if not re.search(r'[0-9_]', original_word) else [original_word]
            for index, word in enumerate(pieces):
                separator = ' ' if index == 0 else ''
                test = (line + separator + word) if line else word
                if line and width(test, size, bold) > limit:
                    result.append(line)
                    line = word
                else:
                    line = test
        result.append(line)
    return result or ['']


def _rects(root, width_, height_):
    out = []
    for node in root.iter():
        if tag(node) != 'rect':
            continue
        x, y = num(node.get('x')), num(node.get('y'))
        w, h = num(node.get('width')), num(node.get('height'))
        if w <= 0 or h <= 0 or (w >= width_ - 1 and h >= height_ - 1):
            continue
        out.append((node, x, y, w, h))
    # A quantitative fill overlay is not the label's box. The common full
    # track is its text owner; its smaller fill keeps the measured bar width.
    return [r for r in out if not any(
        q[3] > r[3] + .1 and abs(q[1]-r[1]) < .1 and abs(q[2]-r[2]) < .1
        and abs(q[4]-r[4]) < .1 for q in out)]


def _interval(group, groups, rects, canvas_width):
    """The smallest containing cell/panel owns padding; neighboring text owns columns."""
    x, y, size, anchor = group.x, group.y, group.size, group.anchor
    candidates = [(w * h, xx, xx + w, yy, yy + h)
                  for _, xx, yy, w, h in rects
                  if xx - .1 <= x <= xx + w + .1 and yy <= y - size * .25 <= yy + h]
    if candidates:
        _, left, right, _, _ = min(candidates)
        # Centered numeric matrix values need their actual cells; table rows
        # spanning most of the canvas need their own text-column boundaries.
        padding = min(8, max(2, (right - left) * .025))
        left += padding
        right -= padding
    else:
        left, right = 12.0, canvas_width - 12.0
    nearby = [g for g in groups if g is not group and
              abs(g.y - y) < max(size, g.size) * .75]
    for other in nearby:
        ox = other.x
        if ox > x + 1 and anchor == 'start':
            right = min(right, ox - 12)
        elif ox < x - 1 and anchor == 'end':
            left = max(left, ox + 12)
        elif anchor == 'middle':
            if ox < x - 1:
                left = max(left, ox + 5 if other.anchor == 'end' else (x + ox) / 2 + 5)
            elif ox > x + 1:
                right = min(right, ox - 5 if other.anchor == 'start' else (x + ox) / 2 - 5)
    # Unboxed row labels stop before the first matrix/bar they precede.
    if not candidates and anchor == 'start':
        for _, xx, yy, w, h in rects:
            if xx > x + 2 and yy <= y <= yy + h:
                right = min(right, xx - 8)
    if anchor == 'start':
        left = max(left, x)
    elif anchor == 'end':
        right = min(right, x)
    else:
        half = min(x - left, right - x)
        left, right = x - half, x + half
    if right - left < size * 1.1:
        # Source labels can sit on a zero-width grid edge. Their neighboring
        # anchor interval, rather than an arbitrary containing rect, owns it.
        left, right = (max(8, x - 85), min(canvas_width - 8, x + 85))
        if anchor == 'start':
            left = x
        elif anchor == 'end':
            right = x
    if right <= left:
        raise LayoutError('cannot resolve text slot for %r' % group.source)
    return left, right


class VerticalMap:
    """Continuous, increasing map; insertion bands contain each old baseline."""
    def __init__(self, insertions):
        # At a common baseline the tallest sibling determines the row growth.
        grouped = {}
        for y, extra, band in insertions:
            key = round(y, 4)
            old = grouped.get(key, (0.0, band))
            grouped[key] = (max(old[0], extra), min(old[1], band))
        self.bands = []
        for y, (extra, band) in sorted(grouped.items()):
            if extra > .001:
                self.bands.append((y, y + max(.1, min(1.0, band)), extra))

    def __call__(self, value):
        shift = 0.0
        for start, end, extra in self.bands:
            if value <= start:
                break
            shift += extra if value >= end else extra * (value - start) / (end - start)
        return value + shift


def _path(d, vertical):
    """Rewrite current SVG path command coordinates, including relative paths."""
    pieces = re.findall(r'[A-Za-z]|[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?', d)
    counts = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'T': 2, 'A': 7, 'Z': 0}
    result, i, command, x, y, sx, sy = [], 0, None, 0.0, 0.0, 0.0, 0.0
    while i < len(pieces):
        if pieces[i].isalpha():
            command = pieces[i]
            i += 1
            if command.upper() not in counts:
                raise LayoutError('unsupported SVG path command %s' % command)
            if command.upper() == 'Z':
                result.append('Z')
                x, y = sx, sy
                continue
        if command is None or command.upper() == 'Z':
            raise LayoutError('malformed SVG path')
        upper, relative = command.upper(), command.islower()
        n = counts[upper]
        if i + n > len(pieces) or any(p.isalpha() for p in pieces[i:i+n]):
            raise LayoutError('malformed SVG coordinate list')
        a = list(map(float, pieces[i:i+n]));i += n
        if upper == 'H':
            x = x + a[0] if relative else a[0]
            result.append('H' + fmt(x))
        elif upper == 'V':
            y = y + a[0] if relative else a[0]
            result.append('V' + fmt(vertical(y)))
        elif upper == 'A':
            # No current figure has arc commands. Nonlinear y reflow cannot
            # preserve an arc's radii exactly, so fail instead of guessing.
            raise LayoutError('arc path requires an explicit quantitative layout')
        else:
            out = []
            for j in range(0, n, 2):
                xx, yy = a[j], a[j+1]
                if relative:
                    xx += x;yy += y
                out.extend((fmt(xx), fmt(vertical(yy))))
            x, y = (x + a[-2], y + a[-1]) if relative else (a[-2], a[-1])
            result.append(upper + ' '.join(out))
            if upper == 'M':
                sx, sy = x, y
                command = 'l' if relative else 'L'
    return ' '.join(result)


def reflow_path(d, vertical):
    # Cover arrows contain tiny three-point open heads as separate subpaths.
    # Keep those heads rigid around their middle (tip) vertex while the
    # connecting route consumes added line height.
    normalized=_path(d,lambda y:y)
    result=[]
    for part in re.split(r'(?=M)',normalized):
        if not part.strip():
            continue
        commands=re.findall(r'[A-Za-z]',part)
        values=[float(n) for n in NUMBER.findall(part)]
        if commands==['M','L','L'] and len(values)==6 and max(values[::2])-min(values[::2])<=16 and max(values[1::2])-min(values[1::2])<=16:
            tip_y=values[3];shift=vertical(tip_y)-tip_y
            result.append(_path(part,lambda y:y+shift))
        else:
            result.append(_path(part,vertical))
    return ' '.join(result)


def geometry_identity(root):
    """Colors, x geometry, highlights, IDs and machine fields, in DOM order."""
    return [(tag(e), tuple(sorted((k, v) for k, v in e.attrib.items()
                                  if k not in Y_ATTRIBUTES)))
            for e in root.iter() if tag(e) in GEOMETRY_TAGS and e.get('data-i18n-annotation') != 'true']


def reflow(source, translations, translate, report=None):
    root = parse(source)
    original = copy.deepcopy(root)
    view = root.get('viewBox', '').split()
    if len(view) != 4 or list(map(float, view[:2])) != [0.0, 0.0]:
        raise LayoutError('expected SVG viewBox with origin 0 0')
    canvas_width, canvas_height = map(float, view[2:])
    groups = rendering_groups(root, text_groups(root))
    rects = _rects(root, canvas_width, canvas_height)
    plans, insertions, fit = [], [], []
    parents = {child: p for p in root.iter() for child in p}

    def translated(group):
        if group.source_parts:
            return ' '.join(translate(part) if translatable(part) else part
                            for part in group.source_parts)
        return translate(group.source) if translatable(group.source) else group.source
    # A very narrow proportional segment keeps its width. Put its category
    # labels in one aligned annotation band, each linked to the same segment.
    callout_rows = {}
    for group in groups:
        if group.anchor != 'middle' or not translatable(group.source):
            continue
        value = translated(group)
        left, right = _interval(group, groups, rects, canvas_width)
        bold = num(group.nodes[0].get('font-weight'), 400) >= 600
        if max(width(word, group.size, bold) for word in re.findall(r'\S+', value)) <= right-left:
            continue
        cells = [r for r in rects if r[1] < group.x < r[1]+r[3]
                 and r[2] <= group.y-group.size*.25 <= r[2]+r[4]]
        if not cells:
            continue
        cell = min(cells, key=lambda r:r[3]*r[4])
        # Ordinary matrix cells can fit one long word with a small readable
        # type adjustment. Only genuinely narrow segments need a callout row.
        if cell[3] < group.size * 5:
            callout_rows.setdefault(round(group.y, 3), (cell[2], []))
    for baseline, (top, _) in list(callout_rows.items()):
        row = [g for g in groups if abs(g.y-baseline)<.01 and g.anchor == 'middle'
               and translatable(g.source)]
        row.sort(key=lambda g:g.x)
        callout_rows[baseline] = (top, row)
    callouts = {}
    for baseline, (top, row) in callout_rows.items():
        slot = (canvas_width-40)/len(row)
        height = 0
        for index, group in enumerate(row):
            value = translated(group)
            lines = wrap(value, slot-14, group.size,
                         num(group.nodes[0].get('font-weight'),400)>=600)
            if any(width(line,group.size)>slot-14 for line in lines):
                raise LayoutError('unbreakable annotation exceeds its label band: %r'%value)
            height=max(height,len(lines)*group.size*1.5+24)
            callouts[id(group)] = (20+(index+.5)*slot, top-1, lines, slot-14)
        insertions.append((top-1, height, 1.0))
    # A mobile matrix can have a 50px Chinese row-heading rail. If a complete
    # English word cannot fit, place that rail's headings above their same
    # numeric rows. Matrix x coordinates and the probability bars stay fixed.
    row_headings = []
    for group in groups:
        if group.anchor != 'start' or id(group) in callouts:
            continue
        cells = [r for r in rects if r[1] > group.x + 2
                 and r[2] <= group.y <= r[2]+r[4]]
        if not cells or any(r[1] <= group.x <= r[1]+r[3] and
                            r[2] <= group.y <= r[2]+r[4] for r in rects):
            continue
        first = min(cells, key=lambda r:r[1])
        if max(r[1]+r[3] for r in cells)-first[1] < canvas_width*.6:
            continue
        row_headings.append((group, first[2]))
    if any(max(width(word,g.size) for word in re.findall(r'\S+',translated(g))) >
           _interval(g,groups,rects,canvas_width)[1]-g.x
           for g,_ in row_headings):
        for group,top in row_headings:
            limit=canvas_width-group.x-18
            lines=wrap(translated(group),limit,group.size,
                       num(group.nodes[0].get('font-weight'),400)>=600)
            callouts[id(group)]=(group.x,top-1,lines,limit,'row-heading')
            insertions.append((top-1,len(lines)*group.size*1.5+14,1.0))
    for group in groups:
        value = translated(group)
        left, right = _interval(group, groups, rects, canvas_width)
        bold = num(group.nodes[0].get('font-weight'), 400) >= 600
        limit = right - left
        x, anchor, size = group.x, group.anchor, group.size
        annotation = callouts.get(id(group))
        if annotation:
            x, _, lines, limit = annotation[:4]
        else:
            lines = wrap(value, limit, size, bold)
        widest = max(width(line, size, bold) for line in lines)
        if widest > limit + .01 and not annotation:
            # Move a label within its existing row before changing type. This
            # commonly gives a right-edge warning its unused left padding.
            cells = [r for r in rects if r[1] <= x <= r[1]+r[3]
                     and r[2] <= group.y-size*.25 <= r[2]+r[4]]
            if anchor == 'start':
                cell=min(cells,key=lambda r:r[3]*r[4]) if cells else None
                min_x=cell[1]+4 if cell else 8
                for other in groups:
                    if other is group or abs(other.y-group.y)>size*.75 or other.x>=x:
                        continue
                    ob=num(other.nodes[0].get('font-weight'),400)>=600
                    ow=width(translated(other),other.size,ob)
                    end=other.x if other.anchor=='end' else other.x+ow/2 if other.anchor=='middle' else other.x+ow
                    min_x=max(min_x,end+10)
                new_x=max(min_x,right-widest)
                if new_x<x:
                    x=new_x;limit=right-x;lines=wrap(value,limit,size,bold)
                    widest=max(width(line,size,bold) for line in lines)
            # At most 15%, never below 14px, solely for an indivisible word.
            if widest>limit+.01 and size>14:
                minimum=max(14.0,group.size*.85)
                candidate=max(minimum,size*limit/widest)
                if candidate<size:
                    size=candidate;lines=wrap(value,limit,size,bold)
                    widest=max(width(line,size,bold) for line in lines)
        if widest > limit + .01:
            raise LayoutError('unbreakable identifier exceeds its source slot (%s/%s): %r' %
                              (fmt(widest), fmt(limit), value))
        line_height = size * 1.5
        last_old = num(group.nodes[-1].get('y'))
        old_span = last_old - group.y
        new_span = (len(lines) - 1) * line_height
        extra = max(0.0, new_span - old_span)
        if not annotation:
            insertions.append((group.y + min(size*.55,8), extra, 1.0))
        plans.append((group, lines, x, anchor, line_height, size, annotation))
        fit.append({'source': group.source, 'width': round(widest, 3),
                    'limit': round(limit, 3), 'lines': len(lines),
                    'font_size': size, 'source_font_size': group.size,
                    'annotation': bool(annotation)})
    vertical = VerticalMap(insertions)
    # A plotted numerical y axis must stay affine. Annotation wrapping may
    # translate the whole plot, but cannot bend its curve or move a point
    # off that curve. Refuse unsupported text growth inside such a plot.
    for element in root.iter():
        if tag(element) != 'polyline':
            continue
        coordinates = [float(n) for n in NUMBER.findall(element.get('points',''))]
        ys = coordinates[1::2]
        if len(ys)>2 and max(ys)>min(ys):
            lo,hi=min(ys),max(ys)
            scale=(vertical(hi)-vertical(lo))/(hi-lo)
            if any(abs(vertical(y)-(vertical(lo)+(y-lo)*scale))>.0001 for y in ys):
                raise LayoutError('English annotation would distort a numerical y axis; give it an external band')
    # All geometry consumes one map. Horizontal attributes remain untouched.
    for element in root.iter():
        kind = tag(element)
        if kind in ('text', 'tspan', 'title', 'desc', 'svg'):
            continue
        for attribute in ('y', 'y1', 'y2', 'cy'):
            if attribute in element.attrib:
                element.set(attribute, fmt(vertical(num(element.get(attribute)))))
        if 'height' in element.attrib:
            old_y = num(element.get('y'))
            # y was just rewritten; obtain the original from parallel nodes.
            index = list(root.iter()).index(element)
            old_element = list(original.iter())[index]
            old_y = num(old_element.get('y'))
            height = num(old_element.get('height'))
            element.set('height', fmt(vertical(old_y + height) - vertical(old_y)))
        if kind in ('polygon', 'polyline'):
            values = [float(n) for n in NUMBER.findall(element.get('points', ''))]
            if len(values) % 2:
                raise LayoutError('odd polygon coordinate count')
            tip_shift=vertical(values[1])-values[1] if kind=='polygon' and values else None
            element.set('points', ' '.join('%s,%s' % (fmt(values[i]), fmt(values[i+1]+tip_shift if tip_shift is not None else vertical(values[i+1])))
                                           for i in range(0, len(values), 2)))
        if kind == 'path':
            element.set('d', reflow_path(element.get('d', ''), vertical))
    for group, lines, x, anchor, line_height, size, annotation in plans:
        element = group.nodes[0]
        for node in group.nodes[1:]:
            parents[node].remove(node)
        for child in list(element):
            element.remove(child)
        element.text = None
        baseline = vertical(annotation[1]) + size + 7 if annotation else vertical(group.y)
        element.set('x', fmt(x));element.set('y', fmt(baseline))
        element.set('font-size', fmt(size))
        if annotation and len(annotation) == 4:
            ET.SubElement(root, '{%s}line' % SVG_NS, {
                'x1':fmt(x), 'y1':fmt(baseline+(len(lines)-1)*line_height+5),
                'x2':fmt(group.x), 'y2':fmt(vertical(annotation[1]+1)+5),
                'stroke':element.get('fill','#536473'), 'stroke-width':'1',
                'data-i18n-annotation':'true'})
        if len(lines) == 1:
            element.text = lines[0]
        else:
            for index, line in enumerate(lines):
                span = ET.SubElement(element, '{%s}tspan' % SVG_NS,
                                     {'x': fmt(x), 'y': fmt(baseline + index * line_height)})
                span.text = line
    for element in root.iter():
        if tag(element) in ('title', 'desc'):
            value = content(element)
            if translatable(value):
                element.text = translate(value)
        if translatable(element.get('aria-label', '')):
            element.set('aria-label', translate(element.get('aria-label')))
    for element in root.iter():
        if tag(element) in ('text', 'tspan'):
            element.set('font-family', 'Arial, \"PingFang SC\", sans-serif')
    style = root.get('style', '')
    style = re.sub(r'font-family\s*:[^;]+;?', '', style)
    root.set('style', style + ';font-family:Arial,\"PingFang SC\",sans-serif')
    new_height = vertical(canvas_height)
    root.set('viewBox', '0 0 %s %s' % (fmt(canvas_width), fmt(new_height)))
    if root.get('height'):
        root.set('height', fmt(new_height))
    for before, after in zip([e for e in original.iter() if tag(e) in ('polygon','polyline','path')],
                             [e for e in root.iter() if tag(e) in ('polygon','polyline','path')]):
        if tag(before) == 'path':
            a=_path(before.get('d',''),lambda y:0)
            b=_path(after.get('d',''),lambda y:0)
        else:
            a=[float(n) for n in NUMBER.findall(before.get('points',''))][::2]
            b=[float(n) for n in NUMBER.findall(after.get('points',''))][::2]
        if a!=b:
            raise LayoutError('layout changed a quantitative horizontal coordinate')
    if [e.get('id') for e in original.iter() if e.get('id')] != [e.get('id') for e in root.iter() if e.get('id')]:
        raise LayoutError('layout changed an SVG ID')
    if geometry_identity(original) != geometry_identity(root):
        raise LayoutError('layout changed horizontal geometry, colors, IDs or machine fields')
    if report is not None:
        report.update(text_blocks=len(plans), wrapped_blocks=sum(len(p[1]) > 1 for p in plans),
                      width=canvas_width, source_height=canvas_height, height=new_height,
                      text_fit=fit, geometry_identity=True, annotation_blocks=len(callouts))
    return ET.tostring(root, encoding='unicode')


def redraw_table(source, rows, translate, report=None):
    """AP diagrams are literal table correspondences; consume the translated table."""
    root = parse(source)
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise LayoutError('AP table must be nonempty and rectangular')
    title = next((e for e in root if tag(e) == 'title'), None)
    if title is None:
        raise LayoutError('AP SVG missing its accessible title')
    title_text = content(title)
    if translatable(title_text):
        title.text = translate(title_text)
    for child in list(root):
        if child is not title:
            root.remove(child)
    count = len(rows[0]);size = 15.0;head_size = 16.0
    # Long prose gains more width than a short status or identifier column.
    weights = [max(100, min(390, max(width(row[j], size) for row in rows)))
               for j in range(count)]
    total = sum(weights)
    minimums = [max(110,max(width(word,16 if i==0 else 15,i==0)
                for i,row in enumerate(rows) for word in re.findall(r'\S+',row[j]))+30)
                for j in range(count)]
    if sum(minimums)>840:
        raise LayoutError('AP identifiers exceed the fixed readable table width')
    remaining=840-sum(minimums)
    widths=[minimums[j]+remaining*weights[j]/total for j in range(count)]
    x_positions = [30.0]
    for w in widths:
        x_positions.append(x_positions[-1] + w)
    cells, y, fit = [], 12.0, []
    for i, row in enumerate(rows):
        fs = head_size if i == 0 else size
        lines = [wrap(value, widths[j] - 30, fs, i == 0) for j, value in enumerate(row)]
        for j, ls in enumerate(lines):
            if any(width(line, fs, i == 0) > widths[j] - 30 + .01 for line in ls):
                raise LayoutError('unbreakable AP table cell: %r' % row[j])
        h = max(len(ls) for ls in lines) * fs * 1.5 + 24
        cells.append((y, h, fs, lines));y += h + 4
        fit.extend({'source': row[j], 'width': round(max(width(line, fs, i == 0) for line in ls), 3),
                    'limit': round(widths[j] - 30, 3), 'lines': len(ls), 'font_size': fs}
                   for j, ls in enumerate(lines))
    height = y + 18
    root.set('viewBox', '0 0 900 %s' % fmt(height))
    ns = '{%s}' % SVG_NS
    ET.SubElement(root, ns + 'rect', {'width': '900', 'height': fmt(height), 'fill': '#fff'})
    for i, (yy, hh, fs, lines) in enumerate(cells):
        if i:
            ET.SubElement(root, ns + 'rect', {'x': '30', 'y': fmt(yy), 'width': '840',
                                             'height': fmt(hh), 'rx': '3',
                                             'fill': '#eaf0f5' if i % 2 else '#f6f8fa'})
        for j, ls in enumerate(lines):
            xx = x_positions[j] + 15
            element = ET.SubElement(root, ns + 'text', {'x': fmt(xx), 'y': fmt(yy + fs + 9),
                'fill': '#233747', 'font-family': 'Arial, \"PingFang SC\", sans-serif', 'font-size': fmt(fs),
                'font-weight': '650' if i == 0 else '400'})
            for k, line in enumerate(ls):
                ET.SubElement(element, ns + 'tspan', {'x': fmt(xx),
                    'y': fmt(yy + fs + 9 + k * fs * 1.5)}).text = line
    if report is not None:
        report.update(table_rows=len(rows), table_columns=count, width=900,
                      height=height, text_fit=fit, translated_table_consumer=True)
    return ET.tostring(root, encoding='unicode')


if __name__ == '__main__':
    print(__doc__)
