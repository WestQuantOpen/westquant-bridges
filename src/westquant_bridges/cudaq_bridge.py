from __future__ import annotations
import subprocess
from pathlib import Path
from typing import Any, Mapping
from westquant_core import RepresentationKind
from .common import BridgeStatus, representation

STATUS = BridgeStatus(
    "cuda-q",
    "alpha",
    False,
    ("program_import", "workload_profile", "execution_hint", "mlir_pass_command", "cudaq_opt_execution"),
    "Native MLIR plugin build must match CUDA-Q/LLVM/MLIR versions.",
)


class CudaQBridge:
    def import_program(self, program: Any, *, representation_id: str = "cudaq:program"):
        text = str(program)
        profile = self.workload_profile(program)
        return representation(
            "cuda-q",
            RepresentationKind.PROGRAM,
            {"text_bytes": len(text), "preview": text[:500], "workload_profile": profile},
            representation_id=representation_id,
            metadata={"native_type": type(program).__name__},
        )

    def workload_profile(self, program: Any, **overrides: Any) -> dict[str, Any]:
        source = program if isinstance(program, Mapping) else getattr(program, "metadata", {})
        source = dict(source) if isinstance(source, Mapping) else {}
        aliases = {
            "num_qubits": "qubits",
            "n_qubits": "qubits",
            "n_1q_gates": "one_qubit_gates",
            "n_2q_gates": "two_qubit_gates",
            "n_observables": "observables",
            "n_parameters": "parameters",
        }
        profile = {aliases.get(key, key): value for key, value in source.items()}
        profile.update(overrides)
        profile.setdefault("workload_id", str(profile.get("name", "cudaq-program")))
        profile.setdefault("qubits", int(getattr(program, "num_qubits", 0) or 0))
        profile.setdefault("depth", int(getattr(program, "depth", 0) or 0))
        profile.setdefault("framework", "cuda-q")
        return profile

    def execution_hint(self, *, engine: str, gpu_count: int = 0, qpu_jobs: int = 0, shots: int = 0, **metadata: Any) -> Any:
        from westquant_core import ExecutionHint
        return ExecutionHint("cuda-q", engine, gpu_count=gpu_count, qpu_jobs=qpu_jobs, shots=shots, metadata=metadata)

    def pass_command(self, input_path: str | Path, plugin_path: str | Path, pass_argument: str, *, cudaq_opt: str = "cudaq-opt") -> list[str]:
        return [cudaq_opt, str(input_path), "--load-cudaq-plugin", str(plugin_path), f"--{pass_argument}"]

    def run_pass(self, *args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        cmd = self.pass_command(*args, **kwargs)
        return subprocess.run(cmd, text=True, capture_output=True, check=False)
