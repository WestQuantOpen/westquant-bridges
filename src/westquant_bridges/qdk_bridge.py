from __future__ import annotations
import json
from typing import Any
from westquant_core import RepresentationKind
from .common import BridgeStatus, representation
STATUS=BridgeStatus('microsoft-qdk','alpha',False,('openqasm_estimate','resource_estimate_import'))
class QDKBridge:
    def estimate_openqasm(self,source:str,params:Any=None):
        from qdk import openqasm
        return openqasm.estimate(source,params=params)
    def import_estimate(self,result:Any,*,representation_id='qdk:estimate'):
        payload={}
        for name in ('physical_counts','logical_qubit','job_params','status'):
            try:
                value=getattr(result,name)
                payload[name]=value() if callable(value) else value
            except Exception: pass
        if not payload:
            try: payload=json.loads(str(result))
            except Exception: payload={'text':str(result)}
        return representation('microsoft-qdk',RepresentationKind.RESOURCE_ESTIMATE,payload,representation_id=representation_id)
