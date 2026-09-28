# experiments/exp6/battery/spec.py
"""Exp 6 rung specs and the generation driver (design §3.1).

Self-contained: nothing here registers into 2c's SPECS (frozen, and
welded to probe machinery this experiment does not use). A rung is a
`RungSpec`; its `draw(rng, ctx, slot)` returns ONE candidate item or
None (rejected). The driver owns de-duplication, the collision gate
against BIG-bench's own strings, the shots and the item count.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

N_EVAL = 500
N_SHOTS = 2
# the shots' slots are N_EVAL and N_EVAL + SHOT_STRIDE. The generators
# cycle their design variables with the slot (periods 2 to 30); at
# consecutive slots the two shots shared the answer's position on four
# rungs and showed only the smallest answers on another. 37 is coprime
# with every period, so the two shots differ in every designed variable.
SHOT_STRIDE = 37
MAX_ATTEMPTS_PER_SLOT = 20_000
WEI_CLASSES = ("E.2", "E.3")
RUNG_TYPES = ("arithmetic", "string", "choice")
OPTIONS_PREFIX = "\nOptions: "


@dataclass(frozen=True)
class RungSpec:
    name: str
    task: str                 # BIG-bench task id (collision-index key)
    wei_class: str            # "E.2" | "E.3"  (Wei et al. 2022, Appendix E)
    rung_type: str            # "arithmetic" | "string" | "choice"
    answer_type: str          # verify_6.ANSWER_TYPES_6
    description: str
    seed: int
    draw: Callable            # draw(rng, ctx, slot) -> dict | None
    n_options: Optional[int] = None   # option-listing rungs only
    collision_kind: str = "input"     # "input" | "target"
    unique_answers: bool = False      # no answer repeats among the 502 (items and shots)


SPECS_6: dict = {}


def validate_spec(spec: RungSpec) -> list:
    from experiments.exp6 import verify_6 as v6
    bad = []
    if spec.wei_class not in WEI_CLASSES:
        bad.append(f"{spec.name}: wei_class {spec.wei_class!r}")
    if spec.rung_type not in RUNG_TYPES:
        bad.append(f"{spec.name}: rung_type {spec.rung_type!r}")
    if spec.answer_type not in v6.ANSWER_TYPES_6:
        bad.append(f"{spec.name}: answer_type {spec.answer_type!r}")
    if spec.collision_kind not in ("input", "target"):
        bad.append(f"{spec.name}: collision_kind {spec.collision_kind!r}")
    if spec.n_options is not None and spec.n_options < 3:
        bad.append(f"{spec.name}: a two-way choice is excluded (design §2 iv)")
    if not spec.name or not spec.description or not spec.task or \
            not callable(spec.draw):
        bad.append(f"{spec.name!r}: name, task, description and draw are mandatory")
    return bad


def register(spec: RungSpec) -> RungSpec:
    bad = validate_spec(spec)
    if bad:
        raise ValueError("; ".join(bad))
    if spec.name in SPECS_6:
        raise ValueError(f"{spec.name} registered twice")
    seeds = {s.seed for s in SPECS_6.values()}
    if spec.seed in seeds:
        raise ValueError(f"{spec.name}: seed {spec.seed} already taken")
    SPECS_6[spec.name] = spec
    return spec


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def with_options(question: str, options) -> str:
    """The option-listing suffix every choice rung uses."""
    opts = [str(o) for o in options]
    if any("," in o or "\n" in o for o in opts):
        raise ValueError(f"an option contains a comma or newline: {opts}")
    return question + OPTIONS_PREFIX + ", ".join(opts)


def check_item(spec: RungSpec, item: dict) -> None:
    from experiments.exp6 import verify_6 as v6
    if not isinstance(item, dict):
        raise ValueError(f"{spec.name}: a draw returned {type(item).__name__}, "
                         f"not a dict")
    for k in ("question", "answer", "bb_key", "meta"):
        if k not in item:
            raise ValueError(f"{spec.name}: item lacks {k!r}")
    for k in ("question", "answer", "bb_key"):
        if not isinstance(item[k], str) or not item[k].strip():
            raise ValueError(f"{spec.name}: {k} is {item[k]!r}, not a non-empty "
                             f"string")
    if not isinstance(item["meta"], dict):
        raise ValueError(f"{spec.name}: meta is {type(item['meta']).__name__}, "
                         f"not a dict")
    try:
        json.dumps(item["meta"])
    except (TypeError, ValueError) as e:
        raise ValueError(f"{spec.name}: meta is not JSON-serialisable ({e})")
    for k in ("question_key", "content_key"):
        v = item.get(k)
        if v is not None and (not isinstance(v, str) or not v.strip()):
            raise ValueError(f"{spec.name}: {k} is {v!r}, not a non-empty string")
    for k in ("guards", "shows"):
        v = item.get(k, [])
        if not isinstance(v, list) or not all(
                isinstance(x, str) and x.strip() for x in v):
            raise ValueError(f"{spec.name}: {k} is {v!r}, not a list of "
                             f"non-empty strings")
    if item.get("guards") and item.get("content_key") is None:
        raise ValueError(f"{spec.name}: guards without a content_key")
    extra = item.get("bb_extra", [])
    if not isinstance(extra, list) or not all(
            isinstance(k, str) and k.strip() for k in extra):
        raise ValueError(f"{spec.name}: bb_extra is {extra!r}, not a list of "
                         f"non-empty strings")
    if item["question"] != item["question"].strip():
        raise ValueError(f"{spec.name}: question has outer whitespace")
    want = v6.normalize_answer_side(item["answer"], spec.answer_type)
    if not v6.exact_under_criterion(item["answer"], spec.answer_type):
        raise ValueError(f"{spec.name}: the criterion truncates answer "
                         f"{item['answer']!r} to {want!r}")
    if spec.n_options is not None:
        if OPTIONS_PREFIX not in item["question"]:
            raise ValueError(f"{spec.name}: option-listing item without options")
        tail = item["question"].rsplit(OPTIONS_PREFIX, 1)[1]
        opts = [v6.normalize_6(o, spec.answer_type) for o in tail.split(", ")]
        if len(opts) != spec.n_options or len(set(opts)) != len(opts):
            raise ValueError(f"{spec.name}: {len(opts)} options listed "
                             f"(distinct {len(set(opts))}), spec says "
                             f"{spec.n_options}")
        if opts.count(want) != 1:
            raise ValueError(f"{spec.name}: answer {want!r} is not exactly one "
                             f"of the options {opts}")
        if item["meta"].get("answer_pos") != opts.index(want) + 1:
            raise ValueError(f"{spec.name}: meta.answer_pos disagrees with "
                             f"the listed options")
    elif OPTIONS_PREFIX in item["question"]:
        raise ValueError(f"{spec.name}: options listed on a rung with "
                         f"n_options None")


def generate(spec: RungSpec, ctx: dict, *, collisions: frozenset,
             collisions_extra: frozenset = frozenset()) -> dict:
    """500 eval items (slots 0..499) then 2 shots (slots 500 and 537),
    one RNG stream. A candidate is REDRAWN (same slot) if the draw rejects,
    its question or its answer-bearing key repeats, its BIG-bench key is
    in the collision index, or one of its EXTRA keys (`bb_extra`: a part
    of the item that is a question in its own right) is in the index's
    extra table.

    Four optional keys of a draw say what the item is, its surface
    aside; the driver reads them and keeps none.
      `question_key`  what the item ASKS (the pair a modarith item asks,
                      either way round; a unit sentence under any
                      subject; a deduction puzzle however its clues are
                      worded; a schedule). No two items of a rung, shots
                      included, carry one question key.
      `content_key`   what would GIVE THE ITEM AWAY if a prompt showed
                      it with its answer.
      `guards`        further keys of the same kind (a unit sentence's
                      numbers in any roles).
      `shows`         what else the item shows beside a result (a
                      modarith item's worked lines), as content keys.
    A SHOT is redrawn, and counted under `shot_content`, if it asks what
    an eval item asks, or if its content key, a guard of its own or a
    key of what it shows is the content key or a guard of an eval item:
    a prompt does not show the answer of an item it is scored on, nor a
    wrong answer to it. An eval item is never redrawn for that."""
    rng = np.random.default_rng(spec.seed)
    seen_q, seen_key, seen_ans = set(), set(), set()
    seen_question, eval_question, eval_content = set(), set(), set()
    n_redrawn = {"rejected": 0, "duplicate": 0, "collision": 0,
                 "shot_answer": 0, "shot_content": 0, "repeated_answer": 0}

    def one(slot, forbid_answers=(), shot=False):
        for _ in range(MAX_ATTEMPTS_PER_SLOT):
            item = spec.draw(rng, ctx, slot)
            if item is None:
                n_redrawn["rejected"] += 1
                continue
            check_item(spec, item)
            key = sha256_text(item["bb_key"])
            asks = item.get("question_key")
            content = item.get("content_key")
            mine = ([] if content is None else [content]) + item.get("guards", [])
            if shot and (asks in eval_question or any(
                    k in eval_content for k in mine + item.get("shows", []))):
                n_redrawn["shot_content"] += 1
                continue
            if item["question"] in seen_q or key in seen_key or asks in seen_question:
                n_redrawn["duplicate"] += 1
                continue
            extra = [sha256_text(k) for k in item.get("bb_extra", [])]
            if key in collisions or any(k in collisions_extra for k in extra):
                n_redrawn["collision"] += 1
                continue
            if item["answer"] in forbid_answers:
                n_redrawn["shot_answer"] += 1
                continue
            if spec.unique_answers and item["answer"] in seen_ans:
                n_redrawn["repeated_answer"] += 1
                continue
            if not shot:
                eval_content.update(mine)
                if asks is not None:
                    eval_question.add(asks)
            if asks is not None:
                seen_question.add(asks)
            seen_q.add(item["question"])
            seen_key.add(key)
            seen_ans.add(item["answer"])
            out = {"question": item["question"], "answer": str(item["answer"]),
                   "bb_sha256": key, "meta": item["meta"]}
            if extra:
                out["bb_extra_sha256"] = extra
            return out
        raise RuntimeError(f"{spec.name}: slot {slot} not filled in "
                           f"{MAX_ATTEMPTS_PER_SLOT} attempts")

    items = [one(slot) for slot in range(N_EVAL)]
    shots, shot_records = [], []
    for j in range(N_SHOTS):
        s = one(N_EVAL + SHOT_STRIDE * j, forbid_answers=tuple(a for _, a in shots),
                shot=True)
        shots.append([s["question"], s["answer"]])
        # a shot is gated like an item; its key and record are kept so the
        # audit can read them (the harness reads `shots` alone)
        shot_records.append({k: v for k, v in s.items()
                             if k not in ("question", "answer")})
    return {"name": spec.name, "task": spec.task, "wei_class": spec.wei_class,
            "rung_type": spec.rung_type, "answer_type": spec.answer_type,
            "description": spec.description, "seed": spec.seed,
            "n_options": spec.n_options, "collision_kind": spec.collision_kind,
            "unique_answers": spec.unique_answers,
            "shots": shots, "shot_records": shot_records,
            "eval_items": items, "n_redrawn": n_redrawn}
