"""Pure arithmetic invoices. No product import, RDF, matcher, parser, or fixture execution.

The caller supplies independent mathematical events. Unknown costs/caps are errors,
never zero. This is i05-fee-events/1-proposal, not an implementation oracle.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib

POOLS = {
    'work': 16777216, 'input_bytes': 262144, 'output_bytes': 262144,
    'trace_items': 8192, 'firings': 1024, 'head_occurrences': 16384, 'bindings': 1024,
}
STRUCTURE = {
    'term_bytes': 16384, 'source_bytes': 65536, 'digits': 4096,
    'integer_bits': 16384, 'temporary_bits': 32768, 'rules': 100,
    'when': 16, 'comparisons': 32, 'heads': 16, 'variables': 64,
}
DOMAIN_ORDER = (
    'work', 'input_bytes', 'output_bytes', 'trace_items', 'firings',
    'head_occurrences', 'bindings', 'scan_copy', 'hash_bytes', 'objects', 'scalar',
)


def nat(value: int) -> int:
    if type(value) is not int or value < 0:
        raise ValueError('expected exact nonnegative integer')
    return value


def limb(value: int) -> int:
    if type(value) is not int:
        raise ValueError('expected exact integer')
    return max(1, (abs(value).bit_length() + 31) // 32)


def allocation(definitions: tuple[tuple[str, bool], ...]) -> list[dict]:
    """Prediction only: caller ordinal preserved; disabled still takes a share."""
    if type(definitions) is not tuple or len(definitions) > 100:
        raise ValueError('invalid definition container/count')
    seen = set()
    for rule_id, disabled in definitions:
        if (type(rule_id) is not str or not rule_id or len(rule_id.encode()) > 16384
                or type(disabled) is not bool or rule_id in seen):
            raise ValueError('invalid/duplicate ID or disabled flag')
        seen.add(rule_id)
    ordered = sorted(enumerate(definitions), key=lambda x: x[1][0])
    if not ordered:
        ordered = [(None, (None, False))]
    n = len(ordered)
    result = []
    for j, (ordinal, (rule_id, disabled)) in enumerate(ordered):
        limits = {k: t // n + int(j < t % n) for k, t in POOLS.items()}
        limits.update(STRUCTURE)
        result.append({'rule_id': rule_id, 'definition_ordinal': ordinal,
                       'disabled': disabled, 'limits': limits})
    return result


def revalidation_caps(children: list[dict]) -> dict:
    return {
        'work': sum(3*c['limits']['work'] + 203 + 33*c['limits']['firings']
                    + 4*c['limits']['output_bytes'] for c in children),
        'input_bytes': sum(2*c['limits']['input_bytes'] for c in children),
        'output_bytes': sum(2*c['limits']['output_bytes'] for c in children),
    }


@dataclass(frozen=True)
class Record:
    fields: tuple[tuple[str, object], ...]


def tlv(value) -> bytes:
    """Independent proposal encoding only; not product typed/canonical codec."""
    def frame(n):
        return nat(n).to_bytes(4, 'big')
    if value is None:
        return b'N'
    if type(value) is bool:
        return b'T' if value else b'F'
    if type(value) is int:
        data = hex(value).encode('ascii')
        return b'I' + frame(len(data)) + data
    if type(value) is str:
        data = value.encode('utf-8', 'strict')
        return b'S' + frame(len(data)) + data
    if type(value) is bytes:
        return b'B' + frame(len(value)) + value
    if type(value) is Record:
        names = [k for k, _ in value.fields]
        if any(type(k) is not str for k in names) or len(set(names)) != len(names):
            raise ValueError('invalid record fields')
        return b'R' + frame(len(value.fields)) + b''.join(tlv(k)+tlv(v) for k, v in value.fields)
    if type(value) is tuple:
        return b'A' + frame(len(value)) + b''.join(tlv(v) for v in value)
    raise ValueError('unsupported proposal value; records use ordered field tuple')


def key_bytes(fields: tuple, source_present: bool) -> bytes:
    """R:93 exact complete key, no parse, no value issuance."""
    if type(fields) is not tuple or len(fields) != 8 or type(source_present) is not bool:
        raise ValueError('invalid key shape')
    if not source_present and any(v is not None for v in fields[4:]):
        raise ValueError('source absent requires four None fields')
    chunks = [b'I05RTK1\x00', bytes([int(source_present)])]
    for value in fields:
        if value is None:
            chunks.append(b'\x00' + b'\x00'*4)
        elif type(value) is str:
            data = value.encode('utf-8', 'strict')
            chunks.append(b'\x01' + len(data).to_bytes(4, 'big') + data)
        else:
            raise ValueError('invalid key field')
    return b''.join(chunks)


def cost(event: dict) -> tuple[dict, tuple[int, int] | None]:
    kind = event['kind']
    if kind == 'item':
        n = nat(event['n'])
        out = {'work': n}
        if 'category' in event:
            if event['category'] not in ('trace_items', 'firings', 'head_occurrences', 'bindings'):
                raise ValueError('invalid item category')
            out[event['category']] = n
        return out, None
    if kind in ('input', 'output', 'scan', 'copy', 'hash', 'mhash'):
        n = nat(event['n'])
        if kind == 'hash':
            return {'hash_bytes': n}, None
        d = {'work': n}
        d[{'input': 'input_bytes', 'output': 'output_bytes', 'scan': 'scan_copy',
           'copy': 'scan_copy', 'mhash': 'hash_bytes'}[kind]] = n
        return d, None
    if kind in ('add', 'sub', 'cmp', 'mul', 'divstep'):
        if kind == 'divstep' and event['b'] == 0:
            raise ValueError('division step requires nonzero divisor')
        a, b = limb(event['a']), limb(event['b'])
        return {'work': a*b if kind in ('mul', 'divstep') else max(a, b)}, None
    if kind == 'shift':
        bits = nat(event['out_bound_bits'])
        return {'work': limb(event['a']) + max(1, (bits+31)//32)}, None
    if kind == 'hold':
        return {}, (nat(event['objects']), nat(event['scalar']))
    if kind == 'finalize':
        h, s, f, b, d = (nat(event[k]) for k in ('handles', 'slots', 'fields', 'bytes', 'domain_bytes'))
        return {'work': f+h+s+2*b, 'scan_copy': 2*b, 'hash_bytes': d+b}, (f+1, b)
    if kind == 'block':
        if type(event.get('proof')) is not str or not event['proof']:
            raise ValueError('block requires independent proof label')
        if not set(event['charges']).issubset(DOMAIN_ORDER[:-2]):
            raise ValueError('unknown block domain')
        return {k: nat(v) for k, v in event['charges'].items()}, None
    if kind in ('error', 'finish', 'release'):
        return {}, None
    raise ValueError('unknown event kind')


def _holds(event: dict) -> list[tuple[str, int, int, bool]]:
    """All retention allocated by an event, including temporary BLOCK live."""
    kind = event['kind']
    if kind == 'hold':
        return [(event['handle'], nat(event['objects']), nat(event['scalar']), False)]
    if kind == 'finalize':
        return [('receipt', nat(event['fields'])+1, nat(event['bytes']), False)]
    if kind == 'block':
        result = []
        if 'live' in event:
            live = event['live']
            if type(live) is not dict or set(live) != {'objects', 'scalar'}:
                raise ValueError('BLOCK live requires exact objects/scalar')
            result.append(('@block:'+event['id'], nat(live['objects']), nat(live['scalar']), True))
        if 'retained' in event:
            retained = event['retained']
            if type(retained) is not dict or set(retained) != {'handle','objects','scalar'}:
                raise ValueError('BLOCK retained requires handle/objects/scalar')
            result.append((retained['handle'], nat(retained['objects']), nat(retained['scalar']), False))
        return result
    return []


def _program(events: list[dict], caps: dict) -> list[tuple]:
    """Static mathematical-program proof, before any ledger opening/mutation.

    No business data or product logic is interpreted. Insufficient cleanup bounds
    are invalid mathematical programs, not runtime resource refusals.
    """
    if type(events) is not list or not events or type(caps) is not dict:
        raise ValueError('exact finite event list/caps required')
    for domain, value in caps.items():
        if domain not in DOMAIN_ORDER:
            raise ValueError('unknown cap domain')
        nat(value)
    fields = {
        'item': ({'n'}, {'category'}),
        'input': ({'n'}, set()), 'output': ({'n'}, set()),
        'scan': ({'n'}, set()), 'copy': ({'n'}, set()),
        'hash': ({'n'}, set()), 'mhash': ({'n'}, set()),
        'add': ({'a','b'}, set()), 'sub': ({'a','b'}, set()),
        'cmp': ({'a','b'}, set()), 'mul': ({'a','b'}, set()),
        'divstep': ({'a','b'}, set()), 'shift': ({'a','out_bound_bits'}, set()),
        'hold': ({'handle','objects','scalar'}, set()),
        'finalize': ({'handles','slots','fields','bytes','domain_bytes'}, set()),
        'block': ({'proof','charges'}, {'live','retained'}),
        'release': ({'handle'}, set()), 'error': ({'reason'}, set()), 'finish': (set(),set()),
    }
    priced, active, ever, ids = [], set(), set(), set()
    final_seen, limits, handles_seen, slots_seen = False, None, 0, 0
    for ordinal, event in enumerate(events):
        if type(event) is not dict or not {'id','kind'}.issubset(event):
            raise ValueError('invalid exact event shape')
        kind, label = event['kind'], event['id']
        if kind not in fields or type(label) is not str or not label or label in ids:
            raise ValueError('unknown event kind/invalid or duplicate event ID')
        ids.add(label)
        required, optional = fields[kind]
        if not ({'id','kind'} | required) <= set(event) <= ({'id','kind'} | required | optional):
            raise ValueError('unknown/missing event field')
        if kind in ('finish','error') and ordinal != len(events)-1:
            raise ValueError('terminal must be the last event; no success prefix')
        if not final_seen and kind not in ('hold','finalize'):
            raise ValueError('data event before finalization prepayment')
        if kind == 'hold' and not final_seen and event['handle'] != 'control':
            raise ValueError('only control bootstrap may precede finalization')
        if kind == 'hold' and final_seen and event['handle'] == 'control':
            raise ValueError('control bootstrap must precede finalization')
        if kind == 'finalize':
            if final_seen:
                raise ValueError('duplicate finalization reservation')
            limits = (nat(event['handles']), nat(event['slots']))
            final_seen = True
        if kind == 'release':
            handle = event['handle']
            if handle in ('control','receipt'):
                raise ValueError('control/receipt retained until terminal cleanup')
            if type(handle) is not str or handle not in active:
                raise ValueError('unknown/released handle')
            active.remove(handle)
        if kind == 'error' and (type(event['reason']) is not str or not event['reason']):
            raise ValueError('error requires bounded mathematical reason')
        charges, _ = cost(event)
        if any(domain not in caps for domain in charges):
            raise ValueError('missing cost cap; not zero')
        holds = _holds(event)
        if holds and not {'objects','scalar'} <= set(caps):
            raise ValueError('missing live caps; not zero')
        for handle, objects, scalar, temporary in holds:
            if type(handle) is not str or not handle or handle in ever:
                raise ValueError('invalid or reused lifetime handle')
            if kind not in ('hold','finalize') and handle in ('control','receipt'):
                raise ValueError('BLOCK cannot alias control/receipt')
            if kind == 'hold' and (handle == 'receipt' or handle.startswith('@')):
                raise ValueError('reserved lifetime handle')
            if handle not in ('control','receipt'):
                # Proof BEFORE active/ever/ledger held/live/peak change.
                if not final_seen or handles_seen+1 > limits[0] or slots_seen+objects > limits[1]:
                    raise ValueError('finalization proof insufficient; incomplete model')
                handles_seen += 1
                slots_seen += objects
            ever.add(handle)
            active.add(handle)
            if temporary:
                active.remove(handle)
        priced.append((event, charges, holds))
    if not final_seen or events[-1]['kind'] not in ('finish','error'):
        raise ValueError('event program has no complete finalization/terminal')
    return priced


@dataclass
class Ledger:
    caps: dict
    state: str = 'new'
    used: dict = field(default_factory=dict)
    live: dict = field(default_factory=lambda: {'objects': 0, 'scalar': 0})
    peak: dict = field(default_factory=lambda: {'objects': 0, 'scalar': 0})
    held: dict = field(default_factory=dict)
    finalized: bool = False
    limits: tuple[int, int] | None = None
    holds_seen: int = 0
    slots_seen: int = 0

    def _cleanup(self, success: bool) -> None:
        # The only place where control/receipt can leave the operation owner.
        keep = {'receipt':self.held['receipt']} if success else {}
        self.held = keep
        self.live = {k:sum(v[j] for v in keep.values())
                     for j,k in enumerate(('objects','scalar'))}

    def run(self, events: list[dict]) -> dict:
        if self.state != 'new':
            raise ValueError('ledger reused; terminal ledger cannot reopen')
        priced = _program(events, self.caps)  # Invalid proof: remains new, no charged/live mutation.
        self.used = {k:0 for k in self.caps if k not in ('objects','scalar')}
        self.state = 'running'
        try:
            for ordinal, (event, charges, holds) in enumerate(priced):
                kind = event['kind']
                attempted = dict(charges)
                if holds:
                    attempted.update({k:self.live[k]+sum(v[j+1] for v in holds)
                                      for j,k in enumerate(('objects','scalar'))})
                # Whole cumulative+temporary+retained vector: all pass, then all commit.
                for domain in DOMAIN_ORDER:
                    if domain not in attempted:
                        continue
                    need = attempted[domain] if domain in self.live else self.used[domain]+attempted[domain]
                    if need > self.caps[domain]:
                        self.state = 'failed'
                        self._cleanup(False)
                        return self.result(event['id'], domain, ordinal, attempted)
                for domain, amount in charges.items():
                    self.used[domain] += amount
                for handle, objects, scalar, temporary in holds:
                    self.held[handle] = (objects,scalar)
                    if handle not in ('control','receipt'):
                        self.holds_seen += 1
                        self.slots_seen += objects
                    self.live['objects'] += objects
                    self.live['scalar'] += scalar
                for domain in self.live:
                    self.peak[domain] = max(self.peak[domain],self.live[domain])
                if kind == 'finalize':
                    self.finalized = True
                    self.limits = (event['handles'],event['slots'])
                for handle, objects, scalar, temporary in holds:
                    if temporary:
                        del self.held[handle]
                        self.live['objects'] -= objects
                        self.live['scalar'] -= scalar
                if kind == 'release':
                    objects, scalar = self.held.pop(event['handle'])
                    self.live['objects'] -= objects
                    self.live['scalar'] -= scalar
                    # Cumulative handles/slots and all paid domains never return.
                if kind in ('error','finish'):
                    self.state = 'failed' if kind == 'error' else 'completed'
                    self._cleanup(kind == 'finish')
                    return self.result(event['id'] if kind == 'error' else None,
                                       event.get('reason') if kind == 'error' else None,ordinal,{})
        except Exception:
            self.state = 'failed'
            self._cleanup(False)
            raise
        raise AssertionError('validated terminal unreachable')

    def result(self, first, domain, ordinal, attempted):
        return {'state':self.state,'used':dict(self.used),'live':dict(self.live),
                'peak':dict(self.peak),'first':first,'domain':domain,
                'ordinal':ordinal,'attempted':attempted,
                'newHandles':self.holds_seen,'newSlots':self.slots_seen}


def proposal_digest(preimage: bytes) -> str:
    if type(preimage) is not bytes:
        raise ValueError('expected independent bytes')
    return hashlib.sha256(b'I05-FEE-PLAN/1\x00' + b'I05FEE1\x00' + preimage).hexdigest()


def restore_bounds(*, b: int, q: int, j: int, n: int, f: int,
                   m: int, u: int, s: int, input_caps: int, output_caps: int) -> dict:
    """R:117-134 conservative domain bounds, not actual usage or a full invoice."""
    for value in (b,q,j,n,f,m,u,s,input_caps,output_caps):
        nat(value)
    if not (b<=8388608 and q<=16777216 and j<=b+q and 1<=n<=100
            and f<=1024 and m<=131072 and m<=128*f and u<=m and s<=16777216 and s<=b+64*m
            and input_caps<=262144 and output_caps<=262144):
        raise ValueError('outside proved R parameter domain')
    return {
        'wire_passes':6*(b+q), 'schema':4096*(b+q+j),
        'traversal':512*j+64*m+65536*n, 'integer_hex':2048*(b+q),
        'scan_copy':64*(b+q+s)+65536*m+65536*n,
        'cache_query':257*(s+m), 'cache_split':512*u,
        'cache_allocation':320*(2*u+n)+64*u+16*m,
        'rule_lookup':(f+2*n+1)*(101*b+n)+65536*n,
        'pv_compare':1048576*m, 'hash':32*b+8*q+s+32*m+65536*n,
        'scalar':16*(b+q+s+65536*m+65536*n)+4096,
        'objects':8*j+16*m+2048*n+4096+256*(2*u+n)+(2*u+n),
        'opaque_scalar':8*(input_caps+output_caps)+(1<<29),
        'opaque_objects':8*(input_caps+output_caps)+4096,
    }


def direct_bounds() -> dict:
    """D's fixed analytic sub-bound plus whole general cap; separate meanings."""
    m,a,s=8388608,250000,100000
    return {'fixed_traversal_subbound':128+8*a+32*s+16*m,
            'objects':128+4*a+12*s+4*(1+8*m), 'scalar':128+2*m+4*m,
            'general_work_cap':64*m+128*(a+s+1),
            'general_scan_copy_cap':64*m+128*(a+s+1)}
