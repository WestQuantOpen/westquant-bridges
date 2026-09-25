from __future__ import annotations
import subprocess
from pathlib import Path
from typing import Any
from westquant_core import RepresentationKind
from .common import BridgeStatus, representation
STATUS=BridgeStatus('cuda-q','alpha',False,('program_import','mlir_pass_command','cudaq_opt_execution'),'Native MLIR plugin build must match CUDA-Q/LLVM/MLIR versions.')
class CudaQBridge:
    def import_program(self,program:Any,*,representation_id='cudaq:program'):
        text=str(program)
        return representation('cuda-q',RepresentationKind.PROGRAM,{'text_bytes':len(text),'preview':text[:500]},representation_id=representation_id,metadata={'native_type':type(program).__name__})
    def pass_command(self,input_path:str|Path,plugin_path:str|Path,pass_argument:str,*,cudaq_opt:str='cudaq-opt')->list[str]:
        return [cudaq_opt,str(input_path),'--load-cudaq-plugin',str(plugin_path),f'--{pass_argument}']
    def run_pass(self,*args:Any,**kwargs:Any)->subprocess.CompletedProcess[str]:
        cmd=self.pass_command(*args,**kwargs)
        return subprocess.run(cmd,text=True,capture_output=True,check=False)
