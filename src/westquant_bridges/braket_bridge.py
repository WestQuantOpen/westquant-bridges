from __future__ import annotations
from collections import Counter
from typing import Any
from westquant_core import RepresentationKind
from .common import BridgeStatus, representation
STATUS=BridgeStatus('amazon-braket','alpha',False,('circuit_import','openqasm_program','local_simulation'))

def circuit_metrics(circuit:Any)->dict[str,Any]:
    instructions=list(getattr(circuit,'instructions',()))
    counts=Counter(type(getattr(i,'operator',i)).__name__ for i in instructions)
    two=sum(len(getattr(i,'target',()))==2 for i in instructions)
    return {'n_instructions':len(instructions),'two_qubit_gates':two,'operations':dict(counts)}
class BraketBridge:
    def import_native(self,circuit:Any,*,representation_id='braket:circuit'):
        return representation('amazon-braket',RepresentationKind.CIRCUIT,circuit_metrics(circuit),representation_id=representation_id)
    def openqasm_program(self,source:str):
        from braket.ir.openqasm import Program
        return Program(source=source)
    def local_run(self,program_or_circuit:Any,*,shots:int=0,backend:str|None=None):
        from braket.devices import LocalSimulator
        device=LocalSimulator(backend) if backend else LocalSimulator()
        return device.run(program_or_circuit,shots=shots).result()
