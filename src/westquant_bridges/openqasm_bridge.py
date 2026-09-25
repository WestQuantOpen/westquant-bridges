from __future__ import annotations
import re
from westquant_core import RepresentationKind
from .common import BridgeStatus, representation
STATUS=BridgeStatus('openqasm','alpha',True,('text_import','static_metrics','verbatim_box'))
GATE_RE=re.compile(r'^\s*([A-Za-z_][\w]*)\s*(?:\([^;]*\))?\s+[^;]+;\s*$',re.M)

def metrics(source:str)->dict:
    qubit_arrays=[int(x) for x in re.findall(r'\bqubit\s*\[(\d+)\]',source)]
    single=len(re.findall(r'\bqubit\s+[A-Za-z_]\w*\s*;',source))
    gates=[g for g in GATE_RE.findall(source) if g not in {'qubit','bit','measure','reset','barrier','input','output'}]
    return {'declared_qubits':sum(qubit_arrays)+single,'gate_statements':len(gates),'measurements':len(re.findall(r'\bmeasure\b',source)),'barriers':len(re.findall(r'\bbarrier\b',source)),'physical_qubit_refs':len(re.findall(r'\$\d+',source)),'verbatim_pragmas':source.count('#pragma braket verbatim')}
class OpenQASMBridge:
    def import_source(self,source:str,*,representation_id='openqasm:program'):
        return representation('openqasm',RepresentationKind.PROGRAM,{**metrics(source),'source':source},representation_id=representation_id)
    def braket_verbatim(self,body:str)->str:
        return 'OPENQASM 3;\n#pragma braket verbatim\nbox {\n'+body.strip()+'\n}\n'
