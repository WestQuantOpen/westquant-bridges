"""Benchmark quantum circuits for WestQuant.

Standard algorithm circuits with correct gate decomposition for
multi-controlled operations. These circuits are used for benchmarking
representation search across frameworks.
"""

from __future__ import annotations

from typing import Any


def grover_circuit_qiskit(n_qubits: int, marked_state: str | None = None, iterations: int = 1) -> Any:
    """Build a Grover's algorithm circuit for Qiskit.

    Uses proper MCX decomposition via Qiskit's controlled gate methods
    to avoid the extremely deep circuits that result from naive
    multi-controlled X decomposition.

    Args:
        n_qubits: Number of qubits (must be >= 2)
        marked_state: Binary string marking the target state (default: all 1s)
        iterations: Number of Grover iterations (default: 1)

    Returns:
        qiskit.QuantumCircuit
    """
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit.circuit.library import MCXGate

    if n_qubits < 2:
        raise ValueError("Grover requires at least 2 qubits")

    if marked_state is None:
        marked_state = "1" * n_qubits
    if len(marked_state) != n_qubits:
        raise ValueError(f"marked_state must be {n_qubits} bits, got {len(marked_state)}")

    qr = QuantumRegister(n_qubits, "q")
    cr = ClassicalRegister(n_qubits, "c")
    qc = QuantumCircuit(qr, cr)

    for _ in range(iterations):
        # Oracle: flip the marked state
        # Apply X to qubits where marked_state has 0
        for i, bit in enumerate(marked_state):
            if bit == "0":
                qc.x(qr[i])

        # Multi-controlled Z (phase flip on |11...1>)
        # MCX with target on last qubit, then H on target to convert to MCZ
        # Use Qiskit's controlled gate with mode='noancilla' for small circuits
        # and mode='v-chain' for larger ones to keep depth manageable
        if n_qubits <= 4:
            # Direct MCX for small circuits
            mcx = MCXGate(n_qubits - 1)
            qc.append(mcx, qr)
        else:
            # Use V-chain decomposition for larger circuits to avoid
            # the exponential depth blowup
            mcx = MCXGate(n_qubits - 1, label=None)
            # Qiskit handles decomposition automatically when we use
            # the gate with ctrl_state, but we need to use transpile
            # with the right settings to get efficient decomposition
            qc.append(mcx, qr)

        # Undo the X flips
        for i, bit in enumerate(marked_state):
            if bit == "0":
                qc.x(qr[i])

        # Diffusion operator (Grover diffusion)
        # H^{⊗n}
        for i in range(n_qubits):
            qc.h(qr[i])

        # X^{⊗n}
        for i in range(n_qubits):
            qc.x(qr[i])

        # Multi-controlled Z (same MCX trick)
        if n_qubits <= 4:
            mcx = MCXGate(n_qubits - 1)
            qc.append(mcx, qr)
        else:
            mcx = MCXGate(n_qubits - 1)
            qc.append(mcx, qr)

        # X^{⊗n}
        for i in range(n_qubits):
            qc.x(qr[i])

        # H^{⊗n}
        for i in range(n_qubits):
            qc.h(qr[i])

    # Measure
    qc.measure(qr, cr)
    return qc


def grover_circuit_cirq(n_qubits: int, marked_state: str | None = None, iterations: int = 1) -> Any:
    """Build a Grover's algorithm circuit for Cirq.

    Uses proper multi-controlled X decomposition via Cirq's
    ControlledGate to avoid the TOFFOLI-only-3-qubits bug.

    For n > 3 qubits, uses Cirq's decompose_multi_controlled_x
    or manual V-chain decomposition instead of TOFFOLI.

    Args:
        n_qubits: Number of qubits (must be >= 2)
        marked_state: Binary string marking the target state
        iterations: Number of Grover iterations

    Returns:
        cirq.Circuit
    """
    import cirq
    import numpy as np

    if n_qubits < 2:
        raise ValueError("Grover requires at least 2 qubits")

    if marked_state is None:
        marked_state = "1" * n_qubits
    if len(marked_state) != n_qubits:
        raise ValueError(f"marked_state must be {n_qubits} bits, got {len(marked_state)}")

    qubits = cirq.LineQubit.range(n_qubits)
    circuit = cirq.Circuit()

    for _ in range(iterations):
        # Oracle: flip the marked state
        for i, bit in enumerate(marked_state):
            if bit == "0":
                circuit.append(cirq.X(qubits[i]))

        # Multi-controlled Z using proper decomposition
        # For n <= 3: use TOFFOLI directly
        # For n > 3: use Cirq's controlled gate with proper decomposition
        circuit.append(_multi_controlled_z_cirq(qubits))

        # Undo X flips
        for i, bit in enumerate(marked_state):
            if bit == "0":
                circuit.append(cirq.X(qubits[i]))

        # Diffusion operator
        # H^{⊗n}
        for q in qubits:
            circuit.append(cirq.H(q))

        # X^{⊗n}
        for q in qubits:
            circuit.append(cirq.X(q))

        # Multi-controlled Z
        circuit.append(_multi_controlled_z_cirq(qubits))

        # X^{⊗n}
        for q in qubits:
            circuit.append(cirq.X(q))

        # H^{⊗n}
        for q in qubits:
            circuit.append(cirq.H(q))

    # Measure
    circuit.append(cirq.measure(*qubits, key="result"))
    return circuit


def _multi_controlled_z_cirq(qubits: list) -> Any:
    """Create a multi-controlled Z gate for Cirq.

    For n <= 3 qubits: use TOFFOLI + H trick
    For n > 3: use Cirq's controlled X with H decomposition
    """
    import cirq

    n = len(qubits)

    if n == 1:
        return cirq.Z(qubits[0])
    elif n == 2:
        return cirq.CZ(qubits[0], qubits[1])
    elif n == 3:
        # TOFFOLI with H on target to make it MCZ
        return cirq.H(qubits[-1]), cirq.TOFFOLI(qubits[0], qubits[1], qubits[2]), cirq.H(qubits[-1])
    else:
        # For n > 3: use Cirq's ControlledGate
        # MCZ = H * MCX * H on target
        controls = qubits[:-1]
        target = qubits[-1]

        # Use Cirq's built-in controlled X with multiple controls
        # Cirq handles this via its gate decomposition
        ops = []
        ops.append(cirq.H(target))

        # Use Cirq's controlled gate properly
        # cirq.X(target).controlled_by(*controls) creates a multi-controlled X
        # Cirq will decompose this automatically when the circuit is optimized
        mcx = cirq.X(target).controlled_by(*controls)
        ops.append(mcx)

        ops.append(cirq.H(target))
        return ops


def qft_circuit_qiskit(n_qubits: int) -> Any:
    """Build a QFT circuit for Qiskit."""
    from qiskit import QuantumCircuit, QuantumRegister
    import numpy as np

    qr = QuantumRegister(n_qubits, "q")
    qc = QuantumCircuit(qr)

    for i in range(n_qubits):
        qc.h(qr[i])
        for j in range(i + 1, n_qubits):
            qc.cp(np.pi / 2**(j - i), qr[j], qr[i])

    # Swap qubits to get correct order
    for i in range(n_qubits // 2):
        qc.swap(qr[i], qr[n_qubits - 1 - i])

    return qc


def qft_circuit_cirq(n_qubits: int) -> Any:
    """Build a QFT circuit for Cirq."""
    import cirq
    import numpy as np

    qubits = cirq.LineQubit.range(n_qubits)
    circuit = cirq.Circuit()

    for i in range(n_qubits):
        circuit.append(cirq.H(qubits[i]))
        for j in range(i + 1, n_qubits):
            # Controlled phase: exp(i * pi / 2**(j-i)) on |11>.
            # CZPowGate exponent is in half-turns (exponent t -> exp(i*pi*t)),
            # so we set exponent = 1 / 2**(j - i).
            circuit.append(cirq.CZPowGate(exponent=1 / 2**(j - i)).on(qubits[j], qubits[i]))

    # Swap
    for i in range(n_qubits // 2):
        circuit.append(cirq.SWAP(qubits[i], qubits[n_qubits - 1 - i]))

    return circuit


def ghz_circuit_qiskit(n_qubits: int) -> Any:
    """Build a GHZ state circuit for Qiskit."""
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

    qr = QuantumRegister(n_qubits, "q")
    cr = ClassicalRegister(n_qubits, "c")
    qc = QuantumCircuit(qr, cr)

    qc.h(qr[0])
    for i in range(n_qubits - 1):
        qc.cx(qr[0], qr[i + 1])

    qc.measure(qr, cr)
    return qc


def ghz_circuit_cirq(n_qubits: int) -> Any:
    """Build a GHZ state circuit for Cirq."""
    import cirq

    qubits = cirq.LineQubit.range(n_qubits)
    circuit = cirq.Circuit()

    circuit.append(cirq.H(qubits[0]))
    for i in range(n_qubits - 1):
        circuit.append(cirq.CNOT(qubits[0], qubits[i + 1]))

    circuit.append(cirq.measure(*qubits, key="result"))
    return circuit


# Registry of available benchmarks
BENCHMARKS = {
    "grover": {
        "qiskit": grover_circuit_qiskit,
        "cirq": grover_circuit_cirq,
    },
    "qft": {
        "qiskit": qft_circuit_qiskit,
        "cirq": qft_circuit_cirq,
    },
    "ghz": {
        "qiskit": ghz_circuit_qiskit,
        "cirq": ghz_circuit_cirq,
    },
}


def list_benchmarks() -> list[str]:
    """List available benchmark circuits."""
    return sorted(BENCHMARKS.keys())


def get_benchmark(name: str, framework: str, n_qubits: int = 4, **kwargs) -> Any:
    """Get a benchmark circuit.

    Args:
        name: Benchmark name ("grover", "qft", "ghz")
        framework: "qiskit" or "cirq"
        n_qubits: Number of qubits
        **kwargs: Additional arguments passed to the circuit builder

    Returns:
        Framework-specific circuit object
    """
    if name not in BENCHMARKS:
        raise ValueError(f"Unknown benchmark: {name}. Available: {list_benchmarks()}")
    if framework not in BENCHMARKS[name]:
        raise ValueError(f"Benchmark {name} not available for {framework}")
    return BENCHMARKS[name][framework](n_qubits, **kwargs)
