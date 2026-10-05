"""Total production stage boundaries; no n/k/B/grid or budget override API."""
from .campaign import Campaign
from .contract import require
from .provenance import LIVE,terminal


def run_collection(root,repo, *, trust_path,trust_sha256,stage,subject=None,backend=LIVE,power_validator=None,git=LIVE):
    def body():
        with Campaign(root,repo,trust_path=trust_path,trust_sha256=trust_sha256,git=git) as c:
            if stage == 'predictor-preflight':
                from .preflight import predictor_preflight
                value = predictor_preflight(c,subject,backend=backend)
            elif stage == 'predictor-collection':
                from .collectors import collect_predictor
                collect_predictor(c,subject,backend=backend)
                value = {'model':subject}
            elif stage == 'predictor-seal':
                from .collectors import seal_predictors
                value = seal_predictors(c)
            elif stage == 'predictor-digest-baseline':
                from .baseline import derive_pythia_baseline
                require(subject is None,'digest baseline has no selector')
                value = derive_pythia_baseline(c)
            elif stage == 'campaign-complete':
                from .collectors import complete_campaign
                require(subject is None,'completion has no selector')
                value = complete_campaign(c)
            elif stage == 'outcome-preflight':
                from .collectors import collect_endpoint
                collect_endpoint(c,subject,backend=backend,power_validator=power_validator)
                value = {'host':subject}
            elif stage == 'outcome-collection':
                from .collectors import collect_outcomes
                require(subject is None,'sweep has no cardinality/grid selector')
                collect_outcomes(c,backend=backend,power_validator=power_validator)
                value = {'checkpoints':26}
            else:
                require(False,'unknown collection stage')
        # Context EXIT validation must finish before COMPLETE is returned.
        return value
    return terminal(root,stage,body)
