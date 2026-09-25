from __future__ import annotations
from typing import Any
from westquant_core import RepresentationKind
from .common import BridgeStatus, representation
STATUS=BridgeStatus('bloqade','alpha',False,('program_import','geometry_context','builder_passthrough'))
class BloqadeBridge:
    def import_program(self,program:Any,*,representation_id='bloqade:program'):
        text=str(program)
        return representation('bloqade',RepresentationKind.CONTROL,{'text_bytes':len(text),'preview':text[:500]},representation_id=representation_id,metadata={'native_type':type(program).__name__})
    def build(self,builder:Any,**parameters:Any): return builder(**parameters) if callable(builder) else builder
