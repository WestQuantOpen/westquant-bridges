from westquant_bridges.search import CirqSequentialSearch, CirqSearchSpace

class Circuit:
    def all_operations(self): return []
    def __len__(self): return getattr(self,'score',5)
class Bridge:
    def compile(self,circuit,**kwargs):
        c=Circuit(); c.score=1 if kwargs['max_num_passes']==2 else 3; return c
    def verify(self,a,b): return {'equivalence':'exact','verified':True}

def test_cirq_search_with_fake_bridge(monkeypatch):
    import westquant_bridges.search as s
    monkeypatch.setattr(s,'cirq_metrics',lambda c:{'two_qubit_gates':c.score,'n_moments':c.score,'n_operations':c.score})
    q=CirqSequentialSearch(gatesets={'g':object()},search_space=CirqSearchSpace(gatesets=('g',),max_passes=(1,2)),beam_width=1,bridge=Bridge())
    r=q.run(Circuit())
    assert r.best is not None
    assert r.best.prefix[-1].parameters['value']==2
