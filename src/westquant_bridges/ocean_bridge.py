from __future__ import annotations
from typing import Any
from westquant_core import RepresentationKind
from .common import BridgeStatus, representation
STATUS=BridgeStatus('dwave-ocean','alpha',False,('bqm_import','embedding_sample','sample_metrics'))

def bqm_metrics(bqm:Any)->dict[str,Any]:
    return {'n_variables':len(getattr(bqm,'variables',())),'n_interactions':len(getattr(bqm,'quadratic',{})),'vartype':str(getattr(bqm,'vartype','unknown'))}
class OceanBridge:
    def import_native(self,bqm:Any,*,representation_id='ocean:bqm'):
        return representation('dwave-ocean',RepresentationKind.HAMILTONIAN,bqm_metrics(bqm),representation_id=representation_id)
    def sample(self,bqm:Any,*,sampler:Any,chain_strength:Any=None,chain_break_method:Any=None,embedding_parameters:dict|None=None,**parameters:Any):
        return sampler.sample(bqm,chain_strength=chain_strength,chain_break_method=chain_break_method,embedding_parameters=embedding_parameters or {},return_embedding=True,**parameters)
    def result_metrics(self,sampleset:Any)->dict[str,Any]:
        energies=list(getattr(getattr(sampleset,'record',None),'energy',()))
        best=min((float(x) for x in energies),default=None)
        cb=getattr(getattr(sampleset,'record',None),'chain_break_fraction',())
        vals=[float(x) for x in cb] if cb is not None else []
        return {'n_samples':len(energies),'best_energy':best,'mean_chain_break_fraction':sum(vals)/len(vals) if vals else None}
