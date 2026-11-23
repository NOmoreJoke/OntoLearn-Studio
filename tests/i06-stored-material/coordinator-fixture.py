"""One explicit same-writer cache-collection fault hook; no added public RPC."""

from ontolearn_engine.__main__ import main
from ontolearn_engine.coordinator import Coordinator

original = Coordinator.dispatch
collected = False


def dispatch(self, method, params):
    global collected
    value = original(self, method, params)
    if method == "result.page" and not collected:
        collected = True
        self.store.collect_cache()
    return value


Coordinator.dispatch = dispatch
main()
