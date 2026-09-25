# westquant-bridges

Experimental framework and IR bridges for WestQuant Open.

## Support Matrix

| Bridge | Status | Description |
|--------|--------|-------------|
| Cirq | EXPERIMENTAL | Circuit import, target-gateset compilation, verification |
| Qibo | EXPERIMENTAL | Circuit import, custom pipeline execution |
| D-Wave Ocean | EXPERIMENTAL | BQM import, embedding/sample controls |
| Amazon Braket | EXPERIMENTAL | Circuit import, OpenQASM Program, local simulation |
| CUDA-Q | EXPERIMENTAL | Program representation, cudaq-opt bridge |
| Bloqade | EXPERIMENTAL | Analog program/geometry builder passthrough |
| Microsoft QDK | EXPERIMENTAL | OpenQASM resource estimation |
| OpenQASM 3.1 | STATIC | Dependency-free static representation/metrics |
| QIR | STATIC | Dependency-free LLVM/QIR static representation/metrics |

**Note:** All SDK-backed bridges are currently EXPERIMENTAL. They have
fake/stub tests only, not native SDK tests. Do not rely on them for
production use yet.

The four primary frameworks (Qiskit, pytket, PennyLane, Pulser) are
SDK_TESTED and available as separate packages:

- `pip install westquant[qiskit]`
- `pip install westquant[pytket]`
- `pip install westquant[pennylane]`
- `pip install westquant[pulser]`

## Installation

```bash
pip install westquant-bridges
```

Every external SDK import is lazy so installing WestQuant bridges does not force
all quantum SDKs into one Python environment.

## License

Apache-2.0
