# westquant-bridges

Wave 5 bridge package for secondary SDKs and common quantum IRs.

Implemented bridge surfaces:

- Cirq: circuit import, target-gateset compilation, small-unitary verification,
  sequential target-gateset/pass search.
- Qibo: circuit import, custom pipeline execution and transpiler assertion hook.
- D-Wave Ocean: BQM import, embedding/sample controls, chain-break/energy metrics,
  embedding search.
- Amazon Braket: circuit import, OpenQASM `Program`, local simulation.
- CUDA-Q: program representation plus `cudaq-opt` external MLIR plugin command
  bridge. Native plugin compilation remains toolchain-version-coupled.
- Bloqade: analog program/geometry builder passthrough.
- Microsoft QDK: OpenQASM resource estimation and resource-result import.
- OpenQASM 3.1: dependency-free static representation/metrics and Braket
  verbatim-box helper.
- QIR: dependency-free LLVM/QIR static representation/metrics.

Every external SDK import is lazy so installing WestQuant bridges does not force
all quantum SDKs into one Python environment.
