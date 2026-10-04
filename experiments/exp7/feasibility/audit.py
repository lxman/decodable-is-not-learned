"""Full-batch checks from independently parsed rendered questions."""
import itertools
import math
import random
import re
from collections import Counter, defaultdict
from fractions import Fraction

from .oracle import solve
from .sources import content, digest
from .generate import bb_surfaces

ARMS = ('q0','q1','q0s','q1s')
FAMILIES = ('words','deduction','units','shapes')


def expected_schedule(family):
    """Independently expand SPEC's schedules; do not call generator.schedule."""
    def shuffled(values, purpose):
        rng = random.Random(int(digest(f'2026100407|{family}|{purpose}'.encode()),16))
        rng.shuffle(values)
        return values
    orientation = shuffled([0]*250+[1]*250,'orientation')
    permutations = list(itertools.permutations(ARMS))
    renders = shuffled(permutations*20+permutations[:20],'render')
    if family == 'deduction':
        assignments = []
        for graph in (0,1):
            for index,positions in enumerate(itertools.combinations(range(5),2)):
                for repeat in range(25):
                    ordered = positions if (repeat+graph+index)%2==0 else positions[::-1]
                    assignments.append((graph,ordered))
    else:
        assignments = list(itertools.permutations(range(5),2))*25
    return orientation,shuffled(assignments,'positions'),renders


def audit(pairs, source, full=True):
    failures, parsed = [], []
    blocks = {f:Counter() for f in FAMILIES}
    cb = {f:dict(orientation=Counter(),positions=Counter(),render=Counter(),a0_labels=Counter(),labels=Counter()) for f in FAMILIES}
    seen_q, seen_id, words = set(), set(), set()
    seen_keys = {f:set() for f in FAMILIES}
    word_reused, bb_checked = 0, 0
    schedules = {family:expected_schedule(family) for family in FAMILIES}

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    for pair in pairs:
        try:
            family = pair['family']
            require(family in FAMILIES,'unknown family')
            require(pair['id'] not in seen_id,'duplicate pair id')
            seen_id.add(pair['id'])
            slot = pair['slot']
            require(type(slot) is int and 0<=slot<500,'slot outside fixed 0..499 coverage')
            require(pair['id']==f'{family}-{slot:04d}','id/slot mismatch')
            require(set(pair['arms'])==set(ARMS),'four arm coverage')
            qs = [pair['arms'][a] for a in ARMS]
            require(len(set(qs))==4 and not any(q in seen_q for q in qs),'duplicate question')
            seen_q.update(qs)
            fs = [solve(family,q,source) for q in qs]
            parsed.append(dict(id=pair['id'],arms=dict(zip(ARMS,fs))))
            require(all(f['ok'] for f in fs),'independent oracle refusal')
            a0,a1 = pair['a0'],pair['a1']
            require(isinstance(a0,str) and isinstance(a1,str) and a0.strip().lower()!=a1.strip().lower(),'targets collide')
            require([f['answer'] for f in fs]==[a0,a1,a0,a1],'oracle/label or sham drift')
            require(all(f['options']==pair['options'] for f in fs),'option order mismatch')
            keys = [content(family,f) for f in fs]
            require(keys==pair['content_keys'],'stored content key mismatch')
            require(not any(k in seen_keys[family] for k in keys),'cross-pair duplicate content')
            seen_keys[family].update(keys)
            surfaces = bb_surfaces(family,fs)
            bb_checked += len(surfaces)+2*len(qs)
            require(source.collision(family,qs,fs,surfaces) is None,'old/BB collision')
            f0,f1,s0,s1 = fs
            latent = pair['latent']
            orientation = pair['orientation']
            require(type(orientation) is int and orientation in (0,1),'orientation invalid')
            if family == 'words':
                require(a0 not in words and a1 not in words,'word reused across pairs')
                words.update((a0,a1))
                word_reused += sum(a in source.word_answers for a in (a0,a1))
                require(len(a0)==len(a1) and 4<=len(a0)<=8,'word length matching')
                ranks = [source.rank[a] for a in (a0,a1)]
                require(all(1<=r<=10000 for r in ranks),'word top10k')
                thirds = [min((r-1)//3333,2) for r in ranks]
                require(thirds[0]==thirds[1] and f0['profile']==f1['profile'],'word tercile/profile matching')
                require(all(f['scrambled']!=f['answer'] for f in fs),'identity scramble')
                require(len({f['scrambled'] for f in fs})==4,'scramble duplication')
                require(latent['natural_words'][::(-1 if orientation else 1)]==[a0,a1],'word orientation')
                base = f'length{len(a0)}:tercile{thirds[0]}'
            elif family == 'deduction':
                require(f0['listed']==f1['listed']==s0['listed']==s1['listed'],'object listing changed')
                require(f0['clue_lines']==f1['clue_lines'] and s0['clue_lines']==s1['clue_lines'],'counterfactual clues changed')
                require(s0['clue_lines']==f0['clue_lines'][1:]+f0['clue_lines'][:1],'sham clue reorder')
                require(f0['order']==f1['order']==s0['order']==s1['order']==latent['order'],'order mismatch')
                require({f0['query'],f1['query']}=={'leftmost','rightmost'},'not opposite endpoints')
                order = f0['order']
                edges = set(map(tuple,f0['edges']))
                chain = set(zip(order,order[1:]))
                g = 0 if edges==chain else 1 if edges==chain|{(order[0],order[2]),(order[2],order[4])} else None
                require(g is not None and g==latent['graph'],'graph class wrong')
                require(a0==order[-1 if orientation else 0],'deduction orientation')
                pos = sorted(pair['options'].index(a)+1 for a in (a0,a1))
                base = f'chain{6 if g else 4}:distance{2 if g else 4}:positions{pos[0]}-{pos[1]}'
            elif family == 'units':
                r0,r1 = f0['roles'],f1['roles']
                require(r0==s0['roles'] and r1==s1['roles'],'unit sham roles changed')
                require(r0['n']==r1['p'] and r0['p']==r1['n'] and r0['Q']==r1['Q'],'not a role swap')
                require(len(set(r0.values()))==3,'numeric roles not distinct')
                require(all(sorted(f['printed'])==sorted(f0['printed']) for f in fs),'quantity multiset mismatch')
                require(all(sorted(re.findall(r'[A-Za-z]+',q))==sorted(re.findall(r'[A-Za-z]+',qs[0])) for q in qs),'unit vocabulary mismatch')
                require(s0['statement_lines']==f0['statement_lines'][1:]+f0['statement_lines'][:1] and s1['statement_lines']==f1['statement_lines'][1:]+f1['statement_lines'][:1],'unit sham reorder')
                n,p = sorted((r0['n'],r0['p']))
                Q = r0['Q']
                m = Fraction(Q,math.lcm(n,p))
                require(2<=n<p<=30 and m.denominator==1 and 2<=m<=12 and Q<=5000,'unit ranges')
                require(latent==dict(n=n,p=p,Q=Q,m=int(m)),'unit latent mismatch')
                require(r0['n']==(p if orientation else n),'unit orientation')
                require(all(a.isdigit() and 0<int(a)<=9999 for a in (a0,a1)),'integer target cap')
                require(len({Fraction(o) for o in pair['options']})==5 and all(Fraction(o)>0 for o in pair['options']),'distinct positive options')
                pool = {Q,n*p,Q+n,Q+p,Q+n+p,p-n,n+p}
                require(set(map(int,pair['options']))-{int(a0),int(a1)} <= pool,'unit filler options')
                d = sorted((len(a0),len(a1)))
                require(tuple(d) in ((2,3),(2,4),(3,3),(3,4),(4,4)),'digit class')
                base = f'multiply_divide:depth2:digits{d[0]}-{d[1]}'
            else:
                require({a0,a1} in ({'square','kite'},{'rectangle','rhombus'}),'shape pair class')
                require(all(f['segments']==4 for f in fs),'segment matching')
                require((4<=len(a0)<=6 and 4<=len(a1)<=6) or (7<=len(a0)<=10 and 7<=len(a1)<=10),'shape length bins')
                classes = ['square','kite'] if 'square' in (a0,a1) else ['rectangle','rhombus']
                require(latent['classes']==classes and classes[::(-1 if orientation else 1)]==[a0,a1],'shape orientation')
                for j,(f,s) in enumerate(((f0,s0),(f1,s1))):
                    pts = [[Fraction(x),Fraction(y)] for x,y in f['points']]
                    sham = [[Fraction(x),Fraction(y)] for x,y in s['points']]
                    require(pts==latent['points'][j],'latent coordinates mismatch')
                    k,dx,dy = latent['sham_transforms'][j]
                    require(k in (1,2,3) and 10<=dx<=40 and 10<=dy<=40,'sham transform range')
                    require(sham==[[x+dx,y+dy] for x,y in pts[k:]+pts[:k]],'sham not translation plus cyclic shift')
                base = 'closed_convex_four_segment:'+':'.join(sorted((a0,a1)))
            require(pair['base_block']==base,'base block mismatch')
            orientations,assignments,renders = schedules[family]
            require(orientation==orientations[slot],'seeded orientation assignment mismatch')
            require(pair['render_order']==list(renders[slot]),'seeded render assignment mismatch')
            if family != 'words':
                assignment = assignments[slot]
                if family == 'deduction':
                    graph,assignment = assignment
                    require(latent['graph']==graph,'seeded graph assignment mismatch')
                require(tuple(pair['options'].index(a) for a in (a0,a1))==assignment,
                        'seeded option assignment mismatch')
            blocks[family][base] += 1
            require(sorted(pair['render_order'])==sorted(ARMS),'render coverage')
            cb[family]['orientation'][str(orientation)] += 1
            cb[family]['render'][','.join(pair['render_order'])] += 1
            cb[family]['a0_labels'][a0] += 1
            cb[family]['labels'].update((a0,a1))
            if pair['options']:
                cb[family]['positions'][','.join(str(pair['options'].index(a)+1) for a in (a0,a1))] += 1
        except (ValueError,KeyError,TypeError,IndexError,AttributeError,ZeroDivisionError) as exc:
            failures.append({'pair':pair.get('id','unknown') if isinstance(pair,dict) else 'invalid','reason':str(exc)})
    counts = Counter(p.get('family') for p in pairs if isinstance(p,dict))
    if full:
        if seen_id != {f'{family}-{slot:04d}' for family in FAMILIES for slot in range(500)}:
            failures.append({'reason':'exact family x slot 0..499 ID coverage'})
        for family in FAMILIES:
            if counts[family]!=500:
                failures.append({'family':family,'reason':'not 500 pairs'})
            expected = {'words':15,'deduction':20,'units':5,'shapes':2}[family]
            if len(blocks[family])!=expected or any(v<10 for v in blocks[family].values()):
                failures.append({'family':family,'reason':'base-block support/coverage'})
            expected_sizes = {'words':[33]*10+[34]*5,'deduction':[25]*20,'units':[100]*5,'shapes':[250]*2}[family]
            if sorted(blocks[family].values())!=expected_sizes:
                failures.append({'family':family,'reason':'base-block quotas'})
            if dict(cb[family]['orientation'])!={'0':250,'1':250}:
                failures.append({'family':family,'reason':'orientation counterbalance'})
            if sorted(cb[family]['render'].values())!=[20]*4+[21]*20:
                failures.append({'family':family,'reason':'render counterbalance'})
            if family!='words' and sorted(cb[family]['positions'].values())!=[25]*20:
                failures.append({'family':family,'reason':'target position counterbalance'})
        if len(words)!=1000:
            failures.append({'reason':'not 1000 disjoint words'})
    source.verify()
    return {'ok':not failures,'failures':failures,'pairs_by_family':dict(counts),'questions':len(seen_q),
            'oracle_questions':sum(len(p['arms']) for p in parsed),'base_blocks':blocks,'counterbalance':cb,
            'old_source_coverage':source.coverage,'old_unique_questions':len(source.questions),
            'old_content_key_counts':{f:len(k) for f,k in source.old.items()},'bb_index_key_counts':source.bb_counts,
            'bb_surface_checks':bb_checked,'collision_failures':sum('collision' in f['reason'] for f in failures),
            'unique_words':len(words),'words_previously_used_as_unscrambling_answers':word_reused,
            'new_content_key_counts':{f:len(k) for f,k in seen_keys.items()},
            'limits':['BIG-bench index supports exact legacy-surface hashes, not unavailable structural content.',
                      'Shapes: four target labels, two quadrilateral pair classes.',
                      'No model results; shortcut scores are descriptive, never item filters.']}, parsed
