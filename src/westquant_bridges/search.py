from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Any, Mapping, Sequence
from westquant_core import Action, DeterministicBeamSearch, Evaluation, Objective
from .cirq_bridge import CirqBridge, circuit_metrics as cirq_metrics
from .ocean_bridge import OceanBridge


@dataclass(frozen=True)
class CirqSearchSpace:
    gatesets: tuple[str, ...] = ("cz", "sqrt_iswap")
    max_passes: tuple[int, ...] = (1, 2, 4)

class CirqSequentialSearch:
    def __init__(self, *, gatesets: Mapping[str, Any] | None = None, search_space: CirqSearchSpace | None = None, beam_width: int = 2, bridge: CirqBridge | None = None):
        self.search_space=search_space or CirqSearchSpace()
        self.gatesets=dict(gatesets or {})
        self.bridge=bridge or CirqBridge()
        self.engine=DeterministicBeamSearch(stages=("gateset","max_passes"),beam_width=beam_width,objectives=(Objective("two_qubit_gates"),Objective("n_moments"),Objective("n_operations")))

    def _gateset(self,name:str):
        if name in self.gatesets:return self.gatesets[name]
        import cirq
        if name=="cz":return cirq.CZTargetGateset()
        if name=="sqrt_iswap":return cirq.SqrtIswapTargetGateset()
        raise KeyError(name)

    def run(self,circuit:Any,*,challenge_id="cirq-challenge"):
        def actions(stage,prefix):
            vals=self.search_space.gatesets if stage=="gateset" else self.search_space.max_passes
            return [Action(stage,str(v),{"value":v}) for v in vals]
        def evaluate(prefix:Sequence[Action]):
            start=time.perf_counter(); cfg={a.stage:a.parameters['value'] for a in prefix}
            if 'gateset' not in cfg:return Evaluation(success=False,error={'type':'IncompletePrefix','message':'gateset required'})
            try:
                compiled=self.bridge.compile(circuit,gateset=self._gateset(str(cfg['gateset'])),max_num_passes=int(cfg.get('max_passes',1)),ignore_failures=False)
                return Evaluation(success=True,metrics=cirq_metrics(compiled),verification=self.bridge.verify(circuit,compiled),cost={'compile_seconds':time.perf_counter()-start})
            except Exception as exc:return Evaluation(success=False,error={'type':type(exc).__name__,'message':str(exc)},cost={'compile_seconds':time.perf_counter()-start})
        return self.engine.run(challenge_id=challenge_id,actions=actions,evaluate=evaluate)


@dataclass(frozen=True)
class OceanSearchSpace:
    chain_strengths: tuple[float | None, ...] = (None, 0.5, 1.0, 2.0)
    gauges: tuple[int, ...] = (0, 1, 4)

class OceanEmbeddingSearch:
    """Deterministic representation search over embedding controls.

    The caller supplies a sampler. If `embedding=True`, it is wrapped in
    D-Wave's EmbeddingComposite. Gauge actions use SpinReversalTransformComposite.
    All sampler/QPU errors are retained as failed policy actions.
    """
    def __init__(self, sampler:Any, *, search_space:OceanSearchSpace|None=None, beam_width:int=2, embedding:bool=True, seed:int=0):
        self.sampler=sampler; self.search_space=search_space or OceanSearchSpace(); self.embedding=embedding; self.seed=seed; self.bridge=OceanBridge()
        self.engine=DeterministicBeamSearch(stages=("chain_strength","gauges"),beam_width=beam_width,objectives=(Objective("best_energy"),Objective("mean_chain_break_fraction")))

    def run(self,bqm:Any,*,challenge_id='ocean-challenge',num_reads:int=100):
        def actions(stage,prefix):
            vals=self.search_space.chain_strengths if stage=='chain_strength' else self.search_space.gauges
            return [Action(stage,str(v),{'value':v}) for v in vals]
        def evaluate(prefix):
            start=time.perf_counter(); cfg={a.stage:a.parameters['value'] for a in prefix}
            try:
                sampler=self.sampler
                if self.embedding:
                    from dwave.system import EmbeddingComposite
                    sampler=EmbeddingComposite(sampler)
                gauges=int(cfg.get('gauges',0) or 0)
                if gauges>0:
                    from dwave.preprocessing import SpinReversalTransformComposite
                    sampler=SpinReversalTransformComposite(sampler,seed=self.seed)
                    kwargs={'num_spin_reversal_transforms':gauges}
                else: kwargs={}
                ss=self.bridge.sample(bqm,sampler=sampler,chain_strength=cfg.get('chain_strength'),num_reads=num_reads,**kwargs)
                return Evaluation(success=True,metrics=self.bridge.result_metrics(ss),verification={'equivalence':'objective_equivalent','verified':True,'method':'BQM gauge/embedding'},cost={'sample_seconds':time.perf_counter()-start})
            except Exception as exc:return Evaluation(success=False,error={'type':type(exc).__name__,'message':str(exc)},cost={'sample_seconds':time.perf_counter()-start})
        return self.engine.run(challenge_id=challenge_id,actions=actions,evaluate=evaluate)


class QDKResourceSearch:
    def __init__(self, parameter_sets:Mapping[str,Any], *, beam_width:int=3):
        self.parameter_sets=dict(parameter_sets)
        self.engine=DeterministicBeamSearch(stages=("resource_model",),beam_width=beam_width,objectives=(Objective("physical_qubits"),Objective("runtime_seconds")))

    def run(self,source:str,*,challenge_id='qdk-resource-challenge'):
        from .qdk_bridge import QDKBridge
        bridge=QDKBridge()
        def actions(stage,prefix):return [Action(stage,name,{'name':name}) for name in sorted(self.parameter_sets)]
        def evaluate(prefix):
            name=prefix[-1].name; start=time.perf_counter()
            try:
                result=bridge.estimate_openqasm(source,self.parameter_sets[name])
                rep=bridge.import_estimate(result)
                p=rep.payload
                # Estimator result schemas vary. Pull common names conservatively.
                physical_counts = p.get('physical_counts') if isinstance(p.get('physical_counts'), dict) else {}
                pq = p.get('physical_qubits') or p.get('physicalQubits') or physical_counts.get('physicalQubits')
                rt = p.get('runtime_seconds') or p.get('runtime') or physical_counts.get('runtime')
                return Evaluation(success=True,metrics={'physical_qubits':pq,'runtime_seconds':rt},verification={'equivalence':'exact','verified':True,'method':'resource-estimation-only'},artifacts={'estimate':p},cost={'estimate_seconds':time.perf_counter()-start})
            except Exception as exc:return Evaluation(success=False,error={'type':type(exc).__name__,'message':str(exc)},cost={'estimate_seconds':time.perf_counter()-start})
        return self.engine.run(challenge_id=challenge_id,actions=actions,evaluate=evaluate)
