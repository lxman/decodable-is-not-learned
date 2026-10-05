# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from dataclasses import asdict
import numpy as np
from exp7core.scoring import Table, Score
from exp7stats.common import SCHEMA, PRODUCTION, KERNEL_VERSION, FAMILIES, PREDICTORS, digest
from exp7stats.data import Predictor, predictor_support
from exp7stats.power import SPEC, grid, cell_id, fit_target, declarations, thin_fixture, SUBSETS, predictor_geometry
from exp7stats.saved_math import VERSION, pack, outcome_summary, BOUND_KEYS
from exp7stats.power_validation import main_record, unrun_record
from exp7stats.calibration import SPEC as CALSPEC, envelope_grid, prompt_probabilities
from exp7stats.envelope_math import envelope_record
from exp7stats.kernels import decision

def predictors(n, mode):
    out = {}
    for p in PREDICTORS:
        ss = tuple((Score(Table(a, 64 - a, 64 - a, a, 64), Table(a, 64 - a, 64 - a, a, 64)) for a in ([i * 64 // n for i in range(n)] if mode == 'varying' else [16 if i < n // 2 else 48 for i in range(n)] if mode == 'blocked' else [32] * n)))
        strata = tuple(('lo' if i < n // 2 else 'hi' for i in range(n))) if mode == 'blocked' else ('all',) * n
        out[p] = Predictor(p, (), tuple(((f, ss) for f in FAMILIES)), tuple(((f, strata) for f in FAMILIES)), ())
    return out

def outcomes(families, subset, nrep, n_positive, m, *, reverse=False):
    result = {}
    for f in subset:
        x = families[f]['x']
        order = sorted(range(len(x)), key=lambda i: x[i], reverse=not reverse)
        y = np.zeros(len(x), dtype=np.int64)
        for j, i in enumerate(order[:n_positive]):
            y[i] = m - j * m // n_positive
        result[f] = pack(np.broadcast_to(y, (nrep, len(y))))
    return result

def envelope(spec=CALSPEC):
    result = {}
    for index, pattern, nf, delta in envelope_grid():
        probabilities = [prompt_probabilities(*v[:2], v[2], delta) for v in pattern]
        if any((v['status'] != 'SUPPORTED' for v in probabilities)) or all((v[0] == 0 or v[1] == 0 for v in pattern)):
            row = envelope_record(index, pattern, nf, delta, spec)
        else:
            counts = []
            for table in probabilities:
                for r in table['rows']:
                    values = [int(64 * q) for q in r]
                    values[max(range(3), key=lambda i: r[i])] += 64 - sum(values)
                    counts.extend(values[:2])
            sample = pack(np.broadcast_to(np.asarray(counts, dtype=np.int64), (spec.n * nf, 8)))
            d = decision(spec.permutations, spec.permutations, spec.permutations)
            bound = {k: d[k] for k in BOUND_KEYS}
            row = envelope_record(index, pattern, nf, delta, spec, samples=[sample] * spec.envelope_replicates, mc=[dict(bound) for _ in range(spec.envelope_replicates)])
        result[row['id']] = row
    return result

def power_record(*, spec=SPEC, n=500, mode='blocked'):
    ps = predictors(n, mode)
    geometry = predictor_geometry(ps)
    rows = {}
    for p, subset, count, m, target in grid(spec):
        families = geometry['predictors'][p]
        name = cell_id(p, subset, count, m, target)
        base = {'id': name, 'predictor': p, 'subset': subset, 'n_positive': count, 'max_count': m, 'target_D': target, 'kernel': KERNEL_VERSION}

        def saved(rho, nrep):
            yy = outcomes(families, subset, nrep, count, m, reverse=rho == 0)
            return outcome_summary(families, subset, yy, nrep, count, m, rho_one=rho == 1)[0]
        fit = {'status': 'SUPPORTED', 'rho': 0.0, 'note': 'prespecified null arm'} if target is None else fit_target(lambda rho: saved(rho, spec.n_cal), lambda rho: saved(rho, spec.n_validate), target, spec)
        if fit['status'] == 'UNSUPPORTED':
            rows[name] = unrun_record(base, fit)
        else:
            yy = outcomes(families, subset, spec.n_sim, count, m, reverse=target is None)
            summary, eligible, extrema = outcome_summary(families, subset, yy, spec.n_sim, count, m)
            bounds = []
            for d, e, limits in zip(summary['Ds'], eligible, extrema):
                if tuple(e['eligible']) != subset:
                    bounds.append({'status': 'EXACT_SUBSET_LOSS', 'eligible': e['eligible']})
                else:
                    b = decision(spec.permutations if d == limits['low'] else 0, spec.permutations, spec.permutations)
                    bounds.append({k: b[k] for k in BOUND_KEYS})
            rows[name] = main_record(base, fit, yy, bounds, families, spec)
    decl = declarations(rows, spec)
    result = {'schema': SCHEMA, 'stage': 'power', 'state': 'COMPLETE', 'production': True, 'saved_math_version': VERSION, 'geometry_sha256': digest(geometry), 'seal_sha256': 'd' * 64, 'battery_sha256': 'a' * 64, 'spec': asdict(spec), 'grid': PRODUCTION.grid, 'rows': rows, 'declarations': decl, 'run_stop_required': any((v['status'] != 'FORECAST-POWERED' for v in decl.values())), 'predictor_support': {p: predictor_support(ps[p]) for p in PREDICTORS}, 'thin_fixtures': {f"{p}/{'-'.join(s)}": thin_fixture(ps[p], s) for p in PREDICTORS for s in SUBSETS}, 'source_bindings': {'code_manifest': '1' * 64, 'source_manifest': '2' * 64, 'calibration': '3' * 64, 'contact_inventory': '4' * 64}, 'calibration_sha256': '3' * 64}
    if spec == SPEC:
        result['selectivity_envelope'] = envelope()
    return (result, geometry)
