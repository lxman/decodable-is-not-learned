"""Independent rendered-question parsers and exact solvers. No generator import."""
import itertools
import re
from collections import Counter
from fractions import Fraction


def options(question):
    body, marker, tail = question.partition('\nOptions: ')
    if not marker:
        return body, []
    opts = tail.split(', ')
    if len(opts) != 5 or len(set(opts)) != 5 or any(not x or '\n' in x for x in opts):
        raise ValueError('five distinct options required')
    return body, opts


def parse_path(text, old=False):
    """Exact M/L path; an M re-statement may not move the current pen."""
    token = r'([ML]) (-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)'
    matches = list(re.finditer(token, text))
    if not matches or ' '.join(m.group(0) for m in matches) != text:
        raise ValueError('unsupported or malformed path')
    points = []
    for i, m in enumerate(matches):
        op, x, y = m.groups()
        p = (Fraction(x), Fraction(y))
        if i == 0:
            if op != 'M':
                raise ValueError('path must start with M')
            points.append(p)
        elif op == 'M':
            if not old or p != points[-1]:
                raise ValueError('pen lift changes geometry')
        else:
            points.append(p)
    if len(points) < 4 or points[-1] != points[0]:
        raise ValueError('path not explicitly closed')
    return points[:-1]


def geometry(points):
    """Strictly convex quadrilateral partition with exact specificity."""
    if len(points) != 4 or len(set(map(tuple, points))) != 4:
        raise ValueError('four distinct vertices required')
    e = [(points[(i+1)%4][0]-p[0], points[(i+1)%4][1]-p[1]) for i, p in enumerate(points)]
    cross = lambda a, b: a[0]*b[1]-a[1]*b[0]
    dot = lambda a, b: a[0]*b[0]+a[1]*b[1]
    turns = [cross(e[i], e[(i+1)%4]) for i in range(4)]
    if not (all(t > 0 for t in turns) or all(t < 0 for t in turns)):
        raise ValueError('degenerate, concave or crossing quadrilateral')
    lengths = [dot(v, v) for v in e]
    right = all(dot(e[i], e[(i+1)%4]) == 0 for i in range(4))
    equal = len(set(lengths)) == 1
    if right and equal:
        return 'square'
    if right:
        return 'rectangle'
    if equal:
        return 'rhombus'
    if any(lengths[i] == lengths[(i+1)%4] and lengths[(i+2)%4] == lengths[(i+3)%4] for i in range(4)):
        return 'kite'
    if sum(cross(e[i], e[i+2]) == 0 for i in (0, 1)) == 1:
        return 'trapezoid'
    raise ValueError('outside the stated partition')


SHAPE_RULE = ('Use the first applicable label: square (four equal sides and four right angles); '
              'rectangle (four right angles); rhombus (four equal sides); '
              'kite (two pairs of adjacent equal sides); trapezoid (exactly one pair of parallel opposite sides).')


def _solve(family, question, source):
    if not isinstance(question, str):
        raise ValueError('question must be text')
    body, opts = options(question)
    facts = {'body': body, 'options': opts}
    if family == 'words':
        m = re.fullmatch(r'Unscramble these letters into one English word: ([a-z]+)\.', body)
        if not m or opts:
            raise ValueError('word grammar')
        scrambled = m[1]
        candidates = source.anagrams.get(''.join(sorted(scrambled)), [])
        if len(candidates) != 1:
            raise ValueError('not exactly one lexicon solution')
        answer = candidates[0]
        facts.update(scrambled=scrambled, rank=source.rank[answer],
                     profile=sorted(Counter(answer).values(), reverse=True))
    elif family == 'deduction':
        lines = body.split('\n')
        m = re.fullmatch(r'Five books stand in a left-to-right row: ([a-z, ]+)\.', lines[0])
        ask = re.fullmatch(r'Which book is (leftmost|rightmost)\?', lines[-1])
        if not m or not ask:
            raise ValueError('deduction header/query grammar')
        listed = m[1].split(', ')
        if len(set(listed)) != 5 or len(listed) != 5 or set(opts) != set(listed):
            raise ValueError('object/options mismatch')
        edges = []
        for line in lines[1:-1]:
            c = re.fullmatch(r'The ([a-z]+) book is (before|after) the ([a-z]+) book\.', line)
            if not c or c[1] not in listed or c[3] not in listed or c[1] == c[3]:
                raise ValueError('invalid relational clue')
            edges.append((c[1], c[3]) if c[2] == 'before' else (c[3], c[1]))
        if len(set(edges)) != len(edges):
            raise ValueError('duplicate clue')
        solutions = []
        for order in itertools.permutations(listed):
            if all(order.index(a) < order.index(b) for a, b in edges):
                solutions.append(order)
        if len(solutions) != 1:
            raise ValueError(f'{len(solutions)} orders instead of one')
        answer = solutions[0][0 if ask[1] == 'leftmost' else -1]
        facts.update(listed=listed, edges=[list(x) for x in edges], order=list(solutions[0]),
                     query=ask[1], clue_lines=lines[1:-1], exhaustive_orders=120)
    elif family == 'units':
        lines = body.split('\n')
        if len(lines) != 5 or lines[0] != 'The machine works at a constant rate; fractional cycles are allowed.' or lines[-1] != 'How many hours are needed to make the required total?':
            raise ValueError('unit header/query grammar')
        patterns = {'n': r'A machine makes (\d+) parts per cycle\.',
                    'p': r'Each cycle lasts (\d+) hours\.',
                    'Q': r'The required total is (\d+) parts\.'}
        roles = {}
        printed = []
        for line in lines[1:4]:
            hits = [(k, re.fullmatch(pattern, line)) for k, pattern in patterns.items()]
            hits = [(k, m) for k, m in hits if m]
            if len(hits) != 1 or hits[0][0] in roles:
                raise ValueError('missing or duplicate dimensional role')
            k, m = hits[0]
            roles[k] = int(m[1])
            printed.append(int(m[1]))
        if any(v <= 0 for v in roles.values()) or len(roles) != 3:
            raise ValueError('nonpositive quantity')
        cycles = Fraction(roles['Q'], roles['n'])
        hours = cycles * roles['p']
        if len({Fraction(o) for o in opts}) != 5 or sum(Fraction(o) == hours for o in opts) != 1:
            raise ValueError('numeric option ambiguity/missing answer')
        answer = str(hours)
        facts.update(roles=roles, printed=printed, statement_lines=lines[1:4], query='hours')
    elif family == 'shapes':
        lines = body.split('\n')
        if len(lines) != 3 or lines[0] != SHAPE_RULE or lines[-1] != 'Which shape does this closed path draw?':
            raise ValueError('shape convention/query grammar')
        m = re.fullmatch(r'<path d="([^"]+)"/>', lines[1])
        if not m:
            raise ValueError('shape path grammar')
        pts = parse_path(m[1])
        answer = geometry(pts)
        if set(opts) != {'square', 'rectangle', 'rhombus', 'kite', 'trapezoid'}:
            raise ValueError('shape option partition mismatch')
        facts.update(points=[[str(x), str(y)] for x, y in pts], path=m[1], query='shape', segments=len(pts))
    else:
        raise ValueError('unknown family')
    if family != 'words' and answer not in opts:
        raise ValueError('answer absent from options')
    return dict(ok=True, answer=answer, **facts)


def solve(family, question, source):
    """Malformed or unsupported input is an explicit refusal, including nontext."""
    try:
        return _solve(family, question, source)
    except (ValueError, TypeError, KeyError, IndexError, ZeroDivisionError, AttributeError) as exc:
        return {'ok': False, 'reason': f'{type(exc).__name__}: {exc}'}
