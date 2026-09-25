from __future__ import annotations
from collections import Counter
from typing import Any
from westquant_core import RepresentationKind
from .common import BridgeStatus, representation

STATUS=BridgeStatus('cirq','alpha',False,('circuit_import','target_gateset_compile','exact_small_verification'))

def circuit_metrics(circuit: Any)->dict[str,Any]:
    ops=list(circuit.all_operations())
    counts=Counter(type(getattr(op,'gate',op)).__name__ for op in ops)
    two=sum(len(getattr(op,'qubits',()))==2 for op in ops)
    return {'n_moments':len(circuit),'n_operations':len(ops),'two_qubit_gates':two,'operations':dict(counts)}

class CirqBridge:
    def import_native(self,circuit:Any,*,representation_id='cirq:circuit'):
        return representation('cirq',RepresentationKind.CIRCUIT,circuit_metrics(circuit),representation_id=representation_id,metadata={'native_type':type(circuit).__name__})
    def compile(self,circuit:Any,*,gateset:Any,max_num_passes:int|None=1,ignore_failures:bool=True):
        import cirq
        return cirq.optimize_for_target_gateset(circuit,gateset=gateset,max_num_passes=max_num_passes,ignore_failures=ignore_failures)
    def verify(self,original:Any,candidate:Any,max_qubits:int=7)->dict[str,Any]:
        try:
            import cirq, numpy as np
            qubits=sorted(set(original.all_qubits())|set(candidate.all_qubits()))
            if len(qubits)>max_qubits:return {'equivalence':'unknown','verified':False,'reason':'unitary_limit'}
            u=cirq.unitary(original,qubit_order=qubits); v=cirq.unitary(candidate,qubit_order=qubits)
            overlap=np.vdot(u.ravel(),v.ravel()); phase=1 if abs(overlap)<1e-15 else overlap/abs(overlap)
            ok=bool(np.allclose(u,phase*v,atol=1e-8,rtol=1e-8))
            return {'equivalence':'exact' if ok else 'invalid','verified':True,'method':'cirq.unitary'}
        except Exception as exc:return {'equivalence':'unknown','verified':False,'reason':type(exc).__name__,'message':str(exc)}
