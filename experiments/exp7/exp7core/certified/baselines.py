"""Fixed rendered-input shortcuts, never given target metadata."""
import math
import re
from collections import Counter
from fractions import Fraction

from .oracle import options, parse_path

METHODS = ('constant', 'position1', 'position2', 'position3', 'position4', 'position5',
           'shortest', 'longest', 'frequency', 'inputcopy', 'absentoption', 'querywordonly',
           'cluedegree', 'endpoint', 'numbers_min', 'numbers_max', 'numbers_sum',
           'numbers_product', 'numbers_ratio', 'segmentcount', 'boundingbox')
FAMILIES = ('words', 'deduction', 'units', 'shapes')


def nonapplicable(method, family):
    if family == 'words' and (method.startswith('position') or method == 'absentoption'):
        return 'no answer options'
    if method == 'frequency' and family == 'units':
        return 'numeric options have no word-frequency ordering'
    if method == 'inputcopy' and family == 'shapes':
        return 'coordinates are not shape-name answers'
    if method in ('cluedegree', 'endpoint') and family != 'deduction':
        return 'no order-clue graph'
    if method.startswith('numbers_') and family != 'units':
        return 'no dimensional quantity statements'
    if method in ('segmentcount', 'boundingbox') and family != 'shapes':
        return 'no geometric path'
    return None


def predict(method, family, question, source):
    if nonapplicable(method, family):
        raise ValueError('nonapplicable baseline must not be scored')
    body, opts = options(question)
    lines = body.split('\n')
    if method == 'constant':
        return {'words':'time','deduction':'red','units':'1','shapes':'square'}[family]
    if method.startswith('position'):
        return opts[int(method[-1])-1]
    if method in ('shortest','longest','frequency'):
        if family == 'words':
            length = len(re.fullmatch(r'Unscramble these letters into one English word: ([a-z]+)\.',body)[1])
            return min((w for w,r in source.rank.items() if r<=10000 and len(w)==length), key=lambda w:source.rank[w])
        if method == 'frequency':
            return min(opts,key=lambda w:source.rank.get(w,math.inf))
        return min(opts,key=lambda w:(-1 if method=='longest' else 1)*len(w))
    if family == 'deduction':
        listed = lines[0].split(': ')[1][:-1].split(', ')
    if method == 'inputcopy':
        if family == 'words':
            return body.split(': ')[1][:-1]
        if family == 'deduction':
            return listed[0]
        return re.search(r'\d+', '\n'.join(lines[1:4]))[0]
    if method == 'absentoption':
        if family == 'shapes':
            statement = lines[1]
        elif family == 'units':
            statement = '\n'.join(lines[1:4])
        else:
            statement = '\n'.join(lines[:-1])
        tokens = re.findall(r'\b\w+\b',statement)
        return next((o for o in opts if o not in tokens),None)
    if method == 'querywordonly':
        if family == 'words':
            return 'time'
        if family == 'deduction':
            return listed[0 if 'leftmost' in lines[-1] else -1]
        return opts[0]
    if method in ('cluedegree','endpoint'):
        edges = []
        for line in lines[1:-1]:
            a,rel,b = re.fullmatch(r'The ([a-z]+) book is (before|after) the ([a-z]+) book\.',line).groups()
            edges.append((a,b) if rel=='before' else (b,a))
        if method == 'cluedegree':
            degree = Counter(v for e in edges for v in e)
            return min(opts,key=lambda o:degree[o])
        excluded = {e[1 if 'leftmost' in lines[-1] else 0] for e in edges}
        return next((o for o in opts if o not in excluded),None)
    if method.startswith('numbers_'):
        numbers = sorted(map(int,re.findall(r'\d+','\n'.join(lines[1:4]))))
        return str({'numbers_min':min(numbers),'numbers_max':max(numbers),
                    'numbers_sum':sum(numbers),'numbers_product':math.prod(numbers),
                    'numbers_ratio':Fraction(max(numbers),min(numbers))}[method])
    path = re.fullmatch(r'<path d="([^"]+)"/>',lines[1])[1]
    pts = parse_path(path)
    if method == 'segmentcount':
        return 'rectangle' if len(pts)==4 else None
    width = max(x for x,y in pts)-min(x for x,y in pts)
    height = max(y for x,y in pts)-min(y for x,y in pts)
    return 'square' if width==height else 'rectangle'


def reading(predictions, a0, a1):
    """Deterministic k=1 analogue; target designation reversal is antisymmetric."""
    supported = [all(predictions[j] in (a0,a1) for j in inds) for inds in ((0,1),(2,3))]
    xs = [int(predictions[j]==a0)-int(predictions[j+1]==a0) if supported[j//2] else 0 for j in (0,2)]
    correct = sum(p == a for p,a in zip(predictions,(a0,a1,a0,a1)))
    wrong = sum(p == a for p,a in zip(predictions,(a1,a0,a1,a0)))
    return {'x':sum(xs)/2,'supported_x_sum':sum(xs), 'supported_renders':sum(supported),
            'unsupported_rows':sum(p not in (a0,a1) for p in predictions),
            'canonical_success':int(predictions[0]==a0 and predictions[1]==a1),
            'sham_success':int(predictions[2]==a0 and predictions[3]==a1),
            'd':(correct-wrong)/4,'u':(correct+wrong)/4,
            'abstentions':sum(p is None for p in predictions)}


def report(pairs, source):
    rows, outputs = [], []
    for family in FAMILIES:
        items = [p for p in pairs if p['family']==family]
        for method in METHODS:
            reason = nonapplicable(method,family)
            row = dict(family=family,method=method,applicable=not bool(reason),reason=reason,
                       pairs=0,paired_success_canonical=None,paired_success_sham=None,
                       mean_x=None,supported_only_x=None,mean_d=None,mean_u=None,
                       prompts=0,emissions=0,abstentions=0,unsupported_rows=0,
                       renders=0,unsupported_renders=0)
            if not reason:
                totals = Counter()
                for p in items:
                    preds = [predict(method,family,p['arms'][arm],source) for arm in ('q0','q1','q0s','q1s')]
                    r = reading(preds,p['a0'],p['a1'])
                    totals.update(r)
                    outputs.append(dict(pair=p['id'],method=method,predictions=preds,reading=r))
                n = len(items)
                row.update(pairs=n,prompts=4*n,renders=2*n,
                           paired_success_canonical=totals['canonical_success'],paired_success_sham=totals['sham_success'],
                           mean_x=totals['x']/n,supported_only_x=totals['supported_x_sum']/totals['supported_renders'] if totals['supported_renders'] else None,
                           mean_d=totals['d']/n,mean_u=totals['u']/n,
                           emissions=4*n-totals['abstentions'],abstentions=totals['abstentions'],
                           unsupported_rows=totals['unsupported_rows'],unsupported_renders=2*n-totals['supported_renders'])
            rows.append(row)
    return rows, outputs
