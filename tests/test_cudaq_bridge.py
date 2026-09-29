from westquant_bridges import CudaQBridge


def test_cudaq_workload_profile_normalizes_aliases():
    profile = CudaQBridge().workload_profile({"name": "demo", "n_qubits": 12, "n_2q_gates": 30}, depth=8)
    assert profile["workload_id"] == "demo"
    assert profile["qubits"] == 12
    assert profile["two_qubit_gates"] == 30
    assert profile["framework"] == "cuda-q"


def test_cudaq_execution_hint_uses_core_contract():
    hint = CudaQBridge().execution_hint(engine="tensor_network", gpu_count=2)
    assert hint.backend_family == "cuda-q"
    assert hint.gpu_count == 2
