from westquant_bridges.openqasm_bridge import metrics as qm
from westquant_bridges.qir_bridge import metrics as irm

def test_openqasm_metrics():
    src='OPENQASM 3;\nqubit[2] q;\nh q[0];\ncx q[0], q[1];\nbit[2] c;\nc = measure q;\n'
    m=qm(src); assert m['declared_qubits']==2 and m['measurements']==1

def test_qir_metrics():
    ir='call void @__quantum__qis__h__body(ptr %q)\ncall void @__quantum__rt__result_record_output(ptr %r, ptr null)'
    m=irm(ir); assert m['qis_calls']==1 and m['runtime_calls']==1
