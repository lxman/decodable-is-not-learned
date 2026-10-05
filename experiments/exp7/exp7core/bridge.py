"""Dependency-injected leaf-call contracts. No defaults, imports or live backend.

This is below the authorization boundary; production composition is BLOCKED
until the separately specified tag/grant/host wrappers exist.
"""
from .contract import ARMS, CAPS, require, sampler_stream


def sample_pair(pair, predictor, *, twin=False, loader, sampler, provenance,
                terminal_ids, device="FAKE"):
    require(callable(loader) and callable(sampler) and callable(provenance),
            "explicit callable injections required; empty injections refuse")
    require(type(terminal_ids) is tuple and terminal_ids
            and len(set(terminal_ids)) == len(terminal_ids)
            and all(type(i) is int and i >= 0 for i in terminal_ids), "terminal IDs")
    mode = "untrained" if twin else "trained"
    specs = [sampler_stream(pair.family, a, predictor, pair.index, twin) for a in ARMS]
    ctx = loader(predictor, mode, device)
    require(type(ctx) is tuple and len(ctx) == 3, "loader shape")
    tok, model, measured = ctx
    require(provenance(measured) is None, "provenance must raise or return None")
    out = {}
    for arm, prompt, spec in zip(ARMS, pair.prompts, specs):
        args = {k: v for k, v in spec.items() if k != "stream_seed"}
        got = sampler(model, tok, prompt, **args,
                      max_new_tokens=CAPS[pair.answer_type], terminal_ids=terminal_ids)
        require(type(got) is dict and set(got) == set(spec["seeds"]), "exact sampler seed keys")
        rows = got[spec["seeds"][0]]
        require(type(rows) is list and len(rows) == spec["draws_per_seed"]
                and all(type(s) is str for s in rows), "exact sampler draw strings")
        out[arm] = tuple(rows)
    return out


def greedy_prompts(prompts, *, loader, runner_factory, provenance, cap):
    require(callable(loader) and callable(runner_factory) and callable(provenance),
            "explicit greedy injections required")
    require(type(prompts) is tuple and prompts and all(type(p) is str for p in prompts),
            "greedy prompt tuple")
    require(cap in CAPS.values(), "greedy cap")
    ctx = loader()
    require(type(ctx) is tuple and len(ctx) == 3, "greedy loader shape")
    model, tok, measured = ctx
    require(provenance(measured) is None, "greedy provenance")
    runner = runner_factory(tok, model)
    require(callable(getattr(runner, "generate", None)), "runner shape")
    got = runner.generate(list(prompts), max_new_tokens=cap)
    require(type(got) is list and len(got) == len(prompts)
            and all(type(s) is str for s in got), "greedy output coverage")
    return tuple(got)
