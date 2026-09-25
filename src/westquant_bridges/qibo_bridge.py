from __future__ import annotations
from collections import Counter
from typing import Any
from westquant_core import RepresentationKind
from .common import BridgeStatus, representation
STATUS=BridgeStatus('qibo','alpha',False,('circuit_import','pipeline_execute','transpile_assert_hook'))

def circuit_metrics(circuit:Any)->dict[str,Any]:
    queue=list(getattr(circuit,'queue',()))
    counts=Counter(type(g).__name__ for g in queue)
    two=sum(len(getattr(g,'qubits',()))==2 for g in queue)
    depth=None
    for name in ('depth','gate_depth'):
        try:
            obj=getattr(circuit,name); depth=int(obj() if callable(obj) else obj); break
        except Exception: pass
    return {'n_qubits':int(getattr(circuit,'nqubits',getattr(circuit,'n_qubits',0))),'n_gates':len(queue),'two_qubit_gates':two,'depth':depth,'operations':dict(counts)}
class QiboBridge:
    def import_native(self,circuit:Any,*,representation_id='qibo:circuit'):
        return representation('qibo',RepresentationKind.CIRCUIT,circuit_metrics(circuit),representation_id=representation_id)
    def compile(self,circuit:Any,*,pipeline:Any):
        result=pipeline(circuit)
        return result if not isinstance(result,tuple) else result[0]
    def verify_transpiling(self,original:Any,candidate:Any,**context:Any)->dict[str,Any]:
        try:
            from qibo.transpiler.asserts import assert_transpiling
            assert_transpiling(original_circuit=original,transpiled_circuit=candidate,**context)
            return {'equivalence':'exact','verified':True,'method':'qibo.assert_transpiling'}
        except Exception as exc:return {'equivalence':'unknown','verified':False,'reason':type(exc).__name__,'message':str(exc)}
