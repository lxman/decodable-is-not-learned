"""Deterministic feasibility constructors; labels come from construction."""
import itertools
import math
import random
from collections import Counter, defaultdict

from .oracle import SHAPE_RULE, solve
from .sources import content, digest

FAMILIES = ('words', 'deduction', 'units', 'shapes')
ARMS = ('q0', 'q1', 'q0s', 'q1s')
COLORS = 'red green blue orange yellow purple black white brown gray'.split()
SHAPES = ['square', 'rectangle', 'rhombus', 'kite', 'trapezoid']
DIGITS = [(2,3), (2,4), (3,3), (3,4), (4,4)]


def stream(family, purpose):
    return random.Random(int(digest(f'2026100407|{family}|{purpose}'.encode()), 16))


def schedule(family):
    orientation = [0]*250 + [1]*250
    stream(family, 'orientation').shuffle(orientation)
    render = list(itertools.permutations(ARMS))*20 + list(itertools.permutations(ARMS))[:20]
    stream(family, 'render').shuffle(render)
    if family == 'deduction':
        positions = []
        for g in range(2):
            for j, (a, b) in enumerate(itertools.combinations(range(5), 2)):
                for k in range(25):
                    positions.append((g, (a,b) if (k+g+j)%2 == 0 else (b,a)))
    else:
        positions = list(itertools.permutations(range(5), 2))*25
    stream(family, 'positions').shuffle(positions)
    return orientation, positions, render


def offered(rng, targets, others, positions):
    others = list(others)
    rng.shuffle(others)
    opts = [None]*5
    for p, a in zip(positions, targets):
        opts[p] = a
    for i in range(5):
        if opts[i] is None:
            opts[i] = others.pop()
    return opts


def with_options(body, opts):
    return body + '\nOptions: ' + ', '.join(opts)


def word_question(scramble):
    return f'Unscramble these letters into one English word: {scramble}.'


def deduction_question(listed, lines, endpoint, opts):
    return with_options('\n'.join(['Five books stand in a left-to-right row: '+', '.join(listed)+'.',
                                  *lines, f'Which book is {endpoint}?']), opts)


def unit_question(n, p, Q, opts, sham=False):
    lines = [f'A machine makes {n} parts per cycle.', f'Each cycle lasts {p} hours.',
             f'The required total is {Q} parts.']
    if sham:
        lines = lines[1:] + lines[:1]
    return with_options('\n'.join(['The machine works at a constant rate; fractional cycles are allowed.',
                                  *lines, 'How many hours are needed to make the required total?']), opts)


def shape_path(points, decimals=False):
    pt = (lambda p: f'{p[0]:.2f},{p[1]:.2f}') if decimals else (lambda p: f'{p[0]},{p[1]}')
    return 'M '+pt(points[0])+' '+' '.join('L '+pt(p) for p in points[1:]+points[:1])


def shape_question(points, opts):
    return with_options(SHAPE_RULE+'\n<path d="'+shape_path(points)+'"/>\nWhich shape does this closed path draw?', opts)


def bb_surfaces(family, facts):
    """Legacy indexed surfaces; exact string checks, not claimed structural BB coverage."""
    out = []
    for f in facts:
        if family == 'words':
            out.append(f"The word {f['scrambled']} is a scrambled version of the English word ")
        elif family == 'deduction':
            parts = [('an ' if c[0] in 'aeiou' else 'a ')+c+' book' for c in f['listed']]
            intro = 'On a shelf, there are five books: '+', '.join(parts[:-1])+', and '+parts[-1]+'.'
            lines = [line.replace('before', 'to the left of').replace('after', 'to the right of') for line in f['clue_lines']]
            out.append(' '.join([intro, *lines]))
        elif family == 'units':
            n, p, Q = (f['roles'][k] for k in ('n','p','Q'))
            out.append(f'A bell rings {n} times every {p} hours. It will ring {Q} times in () hours.')
        else:
            out.append(f'This SVG path element <path d="{f["path"]}"/> draws a ')
            pts = [[int(x),int(y)] for x,y in f['points']]
            out.append(f'This SVG path element <path d="{shape_path(pts, True)}"/> draws a ')
    return out


def shape_draw(rng, label):
    if label == 'square':
        s = rng.randint(6,40)
        pts = [(0,0),(s,0),(s,s),(0,s)]
    elif label == 'rectangle':
        w,h = rng.sample(range(6,41),2)
        pts = [(0,0),(w,0),(w,h),(0,h)]
    elif label == 'rhombus':
        a = rng.randint(2,30)
        b = rng.randint(1,a-1)
        pts = [(0,0),(a,b),(a+b,a+b),(b,a)]
    else:
        a,c = rng.sample(range(6,41),2)
        b = rng.randint(6,40)
        pts = [(0,a),(b,0),(0,-c),(-b,0)]
    transforms = [(r,t) for r in range(1,8) for t in range(8) if math.gcd(r,t)==1]
    r,t = rng.choice(transforms)
    dx,dy = rng.randint(-40,40),rng.randint(-40,40)
    pts = [[r*x-t*y+dx,t*x+r*y+dy] for x,y in pts]
    i = rng.randrange(4)
    return pts[i:]+pts[:i]


def generate(source, attempt_sink=None, per_family=500):
    """per_family<500 is ONLY a deterministic miniature fixture, not a certificate."""
    if not 1 <= per_family <= 500:
        raise ValueError('invalid miniature size')
    attempts = []
    def evidence(row):
        attempts.append(row)
        if attempt_sink:
            attempt_sink(row)
    all_pairs = []
    for family in FAMILIES:
        rng = stream(family, 'content')
        ori, positions, renders = schedule(family)
        seen_keys, seen_q = set(), set()
        pools = {}
        if family == 'words':
            groups = defaultdict(list)
            for w, rank in sorted(source.rank.items(), key=lambda kv:kv[1]):
                if rank <= 10000 and 4 <= len(w) <= 8 and len(source.anagrams[''.join(sorted(w))]) == 1:
                    profile = tuple(sorted(Counter(w).values(), reverse=True))
                    groups[(len(w),min((rank-1)//3333,2),profile)].append(w)
            for (n,t,profile), ws in sorted(groups.items()):
                rng.shuffle(ws)
                pools.setdefault((n,t),[]).extend(zip(ws[::2],ws[1::2]))
            for k in sorted(pools):
                rng.shuffle(pools[k])
            slots = [key for i,key in enumerate(sorted(pools)) for _ in range(34 if i<5 else 33)]
        elif family == 'units':
            pools = {d:[] for d in DIGITS}
            for n in range(2,31):
                for p in range(n+1,31):
                    for m in range(2,13):
                        Q = math.lcm(n,p)*m
                        a,b = Q*p//n,Q*n//p
                        d = tuple(sorted((len(str(a)),len(str(b)))))
                        if Q <= 5000 and max(a,b) <= 9999 and d in pools:
                            pools[d].append((n,p,Q,m))
            for k in sorted(pools):
                rng.shuffle(pools[k])
            slots = [d for d in DIGITS for _ in range(100)]
        for slot in range(per_family):
            for attempt in range(100000):
                orientation = ori[slot]
                opts = []
                if family == 'words':
                    key = slots[slot]
                    if not pools[key]:
                        raise ValueError(f'shortfall words {key}')
                    words = list(pools[key].pop(0))
                    targets = words[::(-1 if orientation else 1)]
                    scrambles = []
                    exhausted = False
                    for w in targets:
                        got = []
                        for draw in range(1000):
                            chars = list(w)
                            rng.shuffle(chars)
                            s = ''.join(chars)
                            reason = ('identity' if s==w else 'repeat_scramble' if s in got else
                                      'old_content' if s in source.old['words'] else
                                      'bigbench_surface' if digest(f'The word {s} is a scrambled version of the English word '.encode()) in source.bb else None)
                            if reason:
                                evidence(dict(family=family,slot=slot,attempt=attempt,word=w,scramble=s,reason=reason))
                            else:
                                got.append(s)
                                if len(got)==2:
                                    break
                        if len(got)!=2:
                            exhausted=True
                            break
                        scrambles.append(got)
                    if exhausted:
                        evidence(dict(family=family,slot=slot,attempt=attempt,words=words,reason='scramble_exhausted'))
                        continue
                    questions = [word_question(s) for s in (scrambles[0][0],scrambles[1][0],scrambles[0][1],scrambles[1][1])]
                    base = f'length{key[0]}:tercile{key[1]}'
                    latent = {'natural_words':words}
                elif family == 'deduction':
                    g,pos = positions[slot]
                    order = rng.sample(COLORS,5)
                    listed = rng.sample(order,5)
                    edges = list(zip(order,order[1:]))
                    if g:
                        edges += [(order[0],order[2]),(order[2],order[4])]
                    lines = [f'The {a} book is before the {b} book.' if rng.randrange(2) else f'The {b} book is after the {a} book.' for a,b in edges]
                    rng.shuffle(lines)
                    targets = [order[0],order[-1]][::(-1 if orientation else 1)]
                    queries = ['leftmost','rightmost'][::(-1 if orientation else 1)]
                    opts = offered(rng,targets,[x for x in order if x not in targets],pos)
                    sham = lines[1:]+lines[:1]
                    questions = [deduction_question(listed,lines,queries[0],opts),deduction_question(listed,lines,queries[1],opts),
                                 deduction_question(listed,sham,queries[0],opts),deduction_question(listed,sham,queries[1],opts)]
                    base = f'chain{6 if g else 4}:distance{2 if g else 4}:positions{min(pos)+1}-{max(pos)+1}'
                    latent = dict(order=order,graph=g)
                elif family == 'units':
                    d = slots[slot]
                    if not pools[d]:
                        raise ValueError(f'shortfall units {d}')
                    n,p,Q,m = pools[d].pop(0)
                    roles = [(n,p,Q),(p,n,Q)][::(-1 if orientation else 1)]
                    targets = [str(Q*p//n),str(Q*n//p)][::(-1 if orientation else 1)]
                    fills = sorted({Q,n*p,Q+n,Q+p,Q+n+p,p-n,n+p}-set(map(int,targets)))
                    opts = offered(rng,targets,list(map(str,rng.sample(fills,3))),positions[slot])
                    questions = [unit_question(*roles[0],opts),unit_question(*roles[1],opts),
                                 unit_question(*roles[0],opts,True),unit_question(*roles[1],opts,True)]
                    base = f'multiply_divide:depth2:digits{d[0]}-{d[1]}'
                    latent = dict(n=n,p=p,Q=Q,m=m)
                else:
                    classes = ('square','kite') if slot<250 else ('rectangle','rhombus')
                    targets = list(classes)[::(-1 if orientation else 1)]
                    opts = offered(rng,targets,[x for x in SHAPES if x not in targets],positions[slot])
                    paths = [shape_draw(rng,label) for label in targets]
                    shams,transforms = [],[]
                    for path in paths:
                        k,dx,dy = rng.randint(1,3),rng.randint(10,40),rng.randint(10,40)
                        shams.append([[x+dx,y+dy] for x,y in path[k:]+path[:k]])
                        transforms.append([k,dx,dy])
                    questions = [shape_question(p,opts) for p in paths+shams]
                    base = 'closed_convex_four_segment:'+':'.join(sorted(classes))
                    latent = dict(classes=list(classes),points=paths,sham_transforms=transforms)
                facts = [solve(family,q,source) for q in questions]
                if any(not f['ok'] for f in facts):
                    evidence(dict(family=family,slot=slot,attempt=attempt,reason='oracle_failure',questions=questions,facts=facts))
                    raise ValueError('construction/oracle disagreement')
                if [f['answer'] for f in facts] != targets*2:
                    raise ValueError('construction labels disagree with independent oracle')
                keys = [content(family,f) for f in facts]
                reason = source.collision(family,questions,facts,bb_surfaces(family,facts))
                if any(k in seen_keys for k in keys):
                    reason = 'new_content'
                if len(set(questions))!=4 or any(q in seen_q for q in questions):
                    reason = 'new_question'
                if reason:
                    evidence(dict(family=family,slot=slot,attempt=attempt,reason=reason,latent=latent,questions=questions,content_keys=keys))
                    continue
                record = dict(id=f'{family}-{slot:04d}',family=family,slot=slot,orientation=orientation,
                              a0=targets[0],a1=targets[1],options=opts,base_block=base,
                              render_order=list(renders[slot]),latent=latent,content_keys=keys,
                              arms=dict(zip(ARMS,questions)))
                seen_keys.update(keys)
                seen_q.update(questions)
                all_pairs.append(record)
                evidence(dict(family=family,slot=slot,attempt=attempt,reason='accepted',pair_id=record['id'],pair=record))
                break
            else:
                raise ValueError(f'shortfall {family} slot{slot}')
    return all_pairs, attempts
