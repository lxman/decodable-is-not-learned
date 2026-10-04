"""Pinned direct inputs and cross-generation content keys (stdlib only)."""
import hashlib
import json
import re
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

from .oracle import parse_path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
WORDS = 'experiments/exp6/battery/data/words_6.tsv'
BB = 'experiments/exp6/battery/data/bigbench_index_6.json'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def textkey(q):
    return ' '.join(q.split('\nOptions:')[0].split())


def geometry_key(points):
    pts = [tuple(map(Fraction, p)) for p in points]
    variants = []
    for seq in (pts, list(reversed(pts))):
        for i in range(len(seq)):
            ring = seq[i:] + seq[:i]
            variants.append(tuple((a[0]-b[0])**2+(a[1]-b[1])**2 for a in ring for b in ring))
    return ','.join(map(str, min(variants)))


def clue_key(edges):
    return ';'.join(a+'<'+b for a, b in sorted(map(tuple, edges)))


def content(family, facts):
    if family == 'words':
        return facts['scrambled']
    if family == 'deduction':
        return '>'.join(facts['order'])
    if family == 'units':
        return ','.join(map(str, sorted(facts['roles'].values())))
    if family == 'shapes':
        return geometry_key(facts['points'])
    raise ValueError(family)


class Sources:
    def __init__(self):
        self.inventory_bytes = (HERE / 'source_inventory.json').read_bytes()
        self.inventory = json.loads(self.inventory_bytes)
        self.verify()
        rows = [line.split('\t') for line in (ROOT/WORDS).read_text().splitlines()[1:]]
        self.rank = {w: int(r) for r, w, _, _ in rows}
        self.anagrams = defaultdict(list)
        for w in self.rank:
            self.anagrams[''.join(sorted(w))].append(w)
        self.questions, self.normalized, self.word_answers = set(), set(), set()
        self.old = {f: set() for f in ('words', 'deduction', 'units', 'shapes')}
        self.old_clues = set()
        self.coverage = {}
        for path in self.inventory['item_files']:
            data = json.loads((ROOT/path).read_bytes())
            counts = Counter()
            name = data.get('name', '')

            def question(q):
                if not isinstance(q, str):
                    raise ValueError('old question not text')
                self.questions.add(q)
                self.normalized.add(textkey(q))
                counts['question_records'] += 1
                for pattern in (r"Unscramble the letters '([a-z]+)'", r'The word ([a-z]+) is a scrambled version'):
                    m = re.search(pattern, q)
                    if m:
                        self.old['words'].add(m[1])
                        counts['word_scramble_keys'] += 1

            def walk(obj):
                if isinstance(obj, dict):
                    if 'question' in obj:
                        question(obj['question'])
                        if 'unscramble' in name:
                            self.word_answers.add(obj.get('answer', ''))
                    # Exp 6 shot_records have meta but no question: their text
                    # is held separately in the shots list. Both surfaces count.
                    if 'meta' in obj:
                        meta = obj['meta']
                        if 'order' in meta and 'clues' in meta:
                            self.old['deduction'].add('>'.join(meta['order']))
                            edges = [(a,b) if k == 'before' else (b,a) for k,a,b in meta['clues'] if k != 'at']
                            # Preserve at clues in the key rather than pretending they are absent.
                            if all(c[0] != 'at' for c in meta['clues']):
                                self.old_clues.add(clue_key(edges))
                            counts['deduction_order_keys'] += 1
                        if 'n' in meta and 'p' in meta and 'shown' in meta:
                            self.old['units'].add(','.join(map(str, sorted((meta['n'],meta['p'],meta['shown'])))))
                            counts['unit_triple_keys'] += 1
                        elif 'r' in meta and 'given' in meta:
                            self.old['units'].add(','.join(map(str, sorted((meta['r'],meta['given'])))))
                            counts['unit_two_number_keys'] += 1
                        if 'path' in meta:
                            try:
                                p = parse_path(meta['path'], old=True)
                                self.old['shapes'].add(geometry_key(p))
                                counts['closed_polygon_keys'] += 1
                            except ValueError:
                                counts['arc_or_open_path_incompatible'] += 1
                    for k, v in obj.items():
                        if k == 'shots' and isinstance(v, list):
                            for shot in v:
                                if isinstance(shot, list) and len(shot) == 2 and isinstance(shot[0], str):
                                    question(shot[0])
                                    if 'unscramble' in name:
                                        self.word_answers.add(shot[1])
                        elif k not in {'feasibility', 'provenance'}:
                            walk(v)
                elif isinstance(obj, list):
                    for value in obj:
                        walk(value)
            walk(data)
            self.coverage[path] = dict(counts)
        bb = json.loads((ROOT/BB).read_bytes())
        if bb['commit'] != '092b196c1f8f14a54bbc62f24759d43bde46dd3b':
            raise ValueError('BB revision mismatch')
        self.bb = set()
        self.bb_counts = {}
        for task, d in bb['tasks'].items():
            if len(d['keys']) != d['n_keys'] or len(set(d['keys'])) != len(d['keys']):
                raise ValueError('BB index coverage')
            self.bb.update(d['keys'])
            self.bb.update(d.get('extra', []))
            self.bb_counts[task] = d['n_keys']

    def verify(self):
        if (HERE/'source_inventory.json').read_bytes() != self.inventory_bytes:
            raise ValueError('inventory changed')
        for path, sha in self.inventory['pins'].items():
            if digest((ROOT/path).read_bytes()) != sha:
                raise ValueError('source hash mismatch: '+path)

    def collision(self, family, questions, facts, bb_surfaces):
        for q in questions:
            if q in self.questions or textkey(q) in self.normalized:
                return 'old_question'
        if any(content(family, f) in self.old[family] for f in facts):
            return 'old_content'
        if family == 'deduction' and any(clue_key(f['edges']) in self.old_clues for f in facts):
            return 'old_clues'
        surfaces = list(questions) + [q.split('\nOptions:')[0] for q in questions] + list(bb_surfaces)
        if any(digest(s.encode()) in self.bb for s in surfaces):
            return 'bigbench_surface'
        return None
