# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import sys
import sysconfig
import types
import _imp
import numpy
from exp7stats.candidate_audit import code_hash
from exp7stats.common import digest

def allowance():
    roots = {'stdlib': Path(sysconfig.get_path('stdlib')).resolve(), 'numpy': Path(numpy.__file__).resolve().parent}
    files, generated, frozen = ({}, {}, {})
    named_modules = tuple(sys.modules.items())
    modules = tuple((v for _, v in named_modules))
    for name, module in named_modules:
        if name and _imp.is_frozen(name):
            frozen[name] = code_hash(_imp.get_frozen_object(name))
        path = getattr(module, '__file__', None)
        if path:
            p = Path(path).resolve()
            role = next((r for r, root in roots.items() if p.is_relative_to(root)), 'helper')
            files[str(p)] = {'sha256': digest(p.read_bytes()), 'role': role}
    for module in modules:
        producer = getattr(module, '__file__', None)
        if not producer:
            continue
        producer = str(Path(producer).resolve())
        if not producer.endswith('.py'):
            continue
        candidates = list(vars(module).values())
        for value in tuple(candidates):
            if isinstance(value, type):
                candidates.extend(vars(value).values())
        for value in candidates:
            if isinstance(value, (classmethod, staticmethod)):
                value = value.__func__
            if isinstance(value, property):
                value = value.fget
            if isinstance(value, types.FunctionType) and value.__code__.co_filename.startswith('<') and (not value.__code__.co_filename.startswith('<frozen')):
                generated[code_hash(value.__code__)] = {'producer': producer, 'producer_sha256': files[producer]['sha256']}
    return {'schema': 'exp7.calibration-runtime.v1', 'roots': {k: str(v) for k, v in roots.items()}, 'files': files, 'generated': generated, 'frozen': frozen}
