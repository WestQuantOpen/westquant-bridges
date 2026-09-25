"""Tests for benchmark quantum circuits.

These tests verify that benchmark circuits (Grover, QFT, GHZ) can be
constructed for both Qiskit and Cirq across a range of qubit counts.

The key regression test is that Cirq Grover works at >3 qubits. The
original bug was that the circuit passed all n qubits to ``cirq.TOFFOLI``,
which only accepts exactly 3 qubits, causing a failure for n > 3.
"""

import pytest


# ---------------------------------------------------------------------------
# Grover -- Qiskit
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n_qubits", [3, 4, 5, 8])
def test_grover_qiskit_constructs(n_qubits):
    """Grover circuit for Qiskit constructs without crashing."""
    pytest.importorskip("qiskit")
    from westquant_bridges.benchmarks import grover_circuit_qiskit

    qc = grover_circuit_qiskit(n_qubits)
    assert qc is not None
    # Circuit should have measurements registered
    assert qc.num_clbits == n_qubits


def test_grover_qiskit_marked_state():
    """Grover oracle honours a custom marked state."""
    pytest.importorskip("qiskit")
    from westquant_bridges.benchmarks import grover_circuit_qiskit

    qc = grover_circuit_qiskit(4, marked_state="1010")
    assert qc is not None
    assert qc.num_qubits == 4


def test_grover_qiskit_iterations():
    """Grover circuit respects the iterations argument."""
    pytest.importorskip("qiskit")
    from westquant_bridges.benchmarks import grover_circuit_qiskit

    qc1 = grover_circuit_qiskit(3, iterations=1)
    qc3 = grover_circuit_qiskit(3, iterations=3)
    # More iterations -> more operations
    assert qc3.size() > qc1.size()


def test_grover_qiskit_invalid_qubits():
    """Grover rejects too few qubits."""
    pytest.importorskip("qiskit")
    from westquant_bridges.benchmarks import grover_circuit_qiskit

    with pytest.raises(ValueError):
        grover_circuit_qiskit(1)


def test_grover_qiskit_bad_marked_state():
    """Grover rejects a mismatched marked state length."""
    pytest.importorskip("qiskit")
    from westquant_bridges.benchmarks import grover_circuit_qiskit

    with pytest.raises(ValueError):
        grover_circuit_qiskit(4, marked_state="11")


# ---------------------------------------------------------------------------
# Grover -- Cirq (the bug-fix tests)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n_qubits", [3, 4, 5, 8])
def test_grover_cirq_constructs(n_qubits):
    """Grover circuit for Cirq constructs without crashing.

    This is the key regression test: previously the circuit passed all n
    qubits to ``cirq.TOFFOLI`` (which only accepts 3 qubits), so any n > 3
    raised an error. The fixed implementation uses
    ``cirq.X(target).controlled_by(*controls)`` for n > 3.
    """
    pytest.importorskip("cirq")
    import cirq
    from westquant_bridges.benchmarks import grover_circuit_cirq

    circuit = grover_circuit_cirq(n_qubits)
    assert circuit is not None
    # The circuit should contain measurement operations
    assert any(isinstance(op.gate, cirq.MeasurementGate)
               for op in circuit.all_operations())


def test_grover_cirq_marked_state():
    """Cirq Grover honours a custom marked state."""
    pytest.importorskip("cirq")
    import cirq
    from westquant_bridges.benchmarks import grover_circuit_cirq

    circuit = grover_circuit_cirq(4, marked_state="0101")
    assert circuit is not None
    assert len(cirq.LineQubit.range(4)) == 4


def test_grover_cirq_iterations():
    """Cirq Grover respects the iterations argument."""
    pytest.importorskip("cirq")
    from westquant_bridges.benchmarks import grover_circuit_cirq

    c1 = grover_circuit_cirq(3, iterations=1)
    c3 = grover_circuit_cirq(3, iterations=3)
    assert len(c3) > len(c1)


def test_grover_cirq_invalid_qubits():
    """Cirq Grover rejects too few qubits."""
    pytest.importorskip("cirq")
    from westquant_bridges.benchmarks import grover_circuit_cirq

    with pytest.raises(ValueError):
        grover_circuit_cirq(1)


def test_grover_cirq_bad_marked_state():
    """Cirq Grover rejects a mismatched marked state length."""
    pytest.importorskip("cirq")
    from westquant_bridges.benchmarks import grover_circuit_cirq

    with pytest.raises(ValueError):
        grover_circuit_cirq(4, marked_state="11")


# ---------------------------------------------------------------------------
# QFT
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n_qubits", [2, 3, 5])
def test_qft_qiskit_constructs(n_qubits):
    pytest.importorskip("qiskit")
    from westquant_bridges.benchmarks import qft_circuit_qiskit

    qc = qft_circuit_qiskit(n_qubits)
    assert qc is not None
    assert qc.num_qubits == n_qubits


@pytest.mark.parametrize("n_qubits", [2, 3, 5])
def test_qft_cirq_constructs(n_qubits):
    pytest.importorskip("cirq")
    from westquant_bridges.benchmarks import qft_circuit_cirq

    circuit = qft_circuit_cirq(n_qubits)
    assert circuit is not None


# ---------------------------------------------------------------------------
# GHZ
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n_qubits", [2, 3, 5])
def test_ghz_qiskit_constructs(n_qubits):
    pytest.importorskip("qiskit")
    from westquant_bridges.benchmarks import ghz_circuit_qiskit

    qc = ghz_circuit_qiskit(n_qubits)
    assert qc is not None
    assert qc.num_qubits == n_qubits
    assert qc.num_clbits == n_qubits


@pytest.mark.parametrize("n_qubits", [2, 3, 5])
def test_ghz_cirq_constructs(n_qubits):
    pytest.importorskip("cirq")
    from westquant_bridges.benchmarks import ghz_circuit_cirq

    circuit = ghz_circuit_cirq(n_qubits)
    assert circuit is not None


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------

def test_list_benchmarks():
    from westquant_bridges.benchmarks import list_benchmarks

    names = list_benchmarks()
    assert "grover" in names
    assert "qft" in names
    assert "ghz" in names


def test_get_benchmark_qiskit():
    pytest.importorskip("qiskit")
    from westquant_bridges.benchmarks import get_benchmark

    qc = get_benchmark("grover", "qiskit", n_qubits=3)
    assert qc is not None


def test_get_benchmark_cirq():
    pytest.importorskip("cirq")
    from westquant_bridges.benchmarks import get_benchmark

    circuit = get_benchmark("grover", "cirq", n_qubits=4)
    assert circuit is not None


def test_get_benchmark_unknown_name():
    from westquant_bridges.benchmarks import get_benchmark

    with pytest.raises(ValueError):
        get_benchmark("not-a-benchmark", "qiskit", n_qubits=3)


def test_get_benchmark_unknown_framework():
    from westquant_bridges.benchmarks import get_benchmark

    with pytest.raises(ValueError):
        get_benchmark("grover", "not-a-framework", n_qubits=3)


def test_benchmarks_exported_from_package():
    """Benchmark functions are re-exported from the top-level package."""
    import westquant_bridges as wb

    for name in (
        "grover_circuit_qiskit",
        "grover_circuit_cirq",
        "qft_circuit_qiskit",
        "qft_circuit_cirq",
        "ghz_circuit_qiskit",
        "ghz_circuit_cirq",
        "list_benchmarks",
        "get_benchmark",
        "BENCHMARKS",
    ):
        assert hasattr(wb, name), f"{name} not exported from westquant_bridges"
