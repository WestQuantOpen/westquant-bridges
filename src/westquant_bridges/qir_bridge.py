from __future__ import annotations
import re
from westquant_core import RepresentationKind
from .common import BridgeStatus, representation
STATUS=BridgeStatus('qir','alpha',True,('llvm_ir_import','static_metrics'))

def metrics(ir:str)->dict:
    qis=re.findall(r'@(__quantum__qis__[^\s(]+)',ir)
    rt=re.findall(r'@(__quantum__rt__[^\s(]+)',ir)
    profiles=re.findall(r'"qir_profiles"\s*=\s*"([^"]+)"',ir)
    return {'qis_calls':len(qis),'runtime_calls':len(rt),'qis_functions':sorted(set(qis)),'runtime_functions':sorted(set(rt)),'profiles':profiles,'bytes':len(ir.encode())}
class QIRBridge:
    def import_ir(self,ir:str,*,representation_id='qir:program'):
        return representation('qir',RepresentationKind.PROGRAM,{**metrics(ir),'llvm_ir':ir},representation_id=representation_id)
