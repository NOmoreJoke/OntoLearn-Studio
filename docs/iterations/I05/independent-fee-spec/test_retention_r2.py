"""R1 F2/F3 regression tests with independent literal mathematical programs."""
import unittest
from invoice_model import Ledger

CAPS = {'work':16777216,'input_bytes':262144,'output_bytes':262144,'trace_items':8192,
        'firings':1024,'head_occurrences':16384,'bindings':1024,'scan_copy':1000,
        'hash_bytes':1000,'objects':100,'scalar':100}
CONTROL = {'id':'C','kind':'hold','handle':'control','objects':64,'scalar':0}
DONE = {'id':'done','kind':'finish'}


def final(h,s):
    return {'id':'F','kind':'finalize','handles':h,'slots':s,'fields':2,'bytes':3,'domain_bytes':1}


def hold(name,o=1,s=2):
    return {'id':name,'kind':'hold','handle':name,'objects':o,'scalar':s}


def release(name,label=None):
    return {'id':label or 'drop-'+name,'kind':'release','handle':name}


class RetentionRegressions(unittest.TestCase):
    def invalid_before_open(self, program):
        ledger=Ledger(CAPS)
        with self.assertRaises(ValueError):
            ledger.run(program)
        self.assertEqual(ledger.state,'new')
        self.assertEqual(ledger.used,{})
        self.assertEqual(ledger.held,{})
        self.assertEqual(ledger.live,{'objects':0,'scalar':0})
        self.assertEqual(ledger.peak,{'objects':0,'scalar':0})
        self.assertEqual((ledger.holds_seen,ledger.slots_seen),(0,0))

    def test_control_objects_67_68_literal(self):
        program=[CONTROL,final(1,1),hold('x'),DONE]
        denied=Ledger(CAPS|{'objects':67}).run(program)
        self.assertEqual((denied['state'],denied['first'],denied['domain']),('failed','x','objects'))
        self.assertEqual(denied['used']['work'],10)
        self.assertEqual(denied['peak'],{'objects':67,'scalar':3})
        self.assertEqual(denied['live'],{'objects':0,'scalar':0})
        self.assertEqual((denied['newHandles'],denied['newSlots']),(0,0))
        enough=Ledger(CAPS|{'objects':68}).run(program)
        self.assertEqual(enough['state'],'completed')
        self.assertEqual(enough['peak'],{'objects':68,'scalar':5})
        self.assertEqual(enough['live'],{'objects':3,'scalar':3})
        self.assertEqual(enough['used']['work'],10)

    def test_control_release_and_alias_never_free_bootstrap(self):
        self.invalid_before_open([CONTROL,final(1,1),release('control'),hold('x'),DONE])
        self.invalid_before_open([CONTROL,final(1,1),release('control','early'),
                                  release('control','again'),hold('x'),DONE])
        self.invalid_before_open([CONTROL,final(1,1),hold('x')|{'aliasOf':'control'},DONE])
        self.invalid_before_open([final(1,1),CONTROL,hold('x'),DONE])
        self.invalid_before_open([CONTROL,final(1,1),release('receipt'),DONE])

    def test_h0_s0_and_one_zero_reject_without_any_mutation(self):
        for h,s in ((0,0),(0,1),(1,0)):
            with self.subTest(h=h,s=s):
                self.invalid_before_open([final(h,s),hold('x'),DONE])

    def test_last_allowed_handle_and_slot_literal(self):
        one=Ledger(CAPS|{'objects':4,'scalar':5}).run([final(1,1),hold('x'),DONE])
        self.assertEqual(one['state'],'completed')
        self.assertEqual((one['newHandles'],one['newSlots']),(1,1))
        self.assertEqual(one['peak'],{'objects':4,'scalar':5})
        self.assertEqual(one['used']['work'],10)
        exact=Ledger(CAPS|{'objects':6,'scalar':3}).run(
            [final(2,3),hold('a',2,0),hold('b',1,0),DONE])
        self.assertEqual(exact['state'],'completed')
        self.assertEqual((exact['newHandles'],exact['newSlots']),(2,3))
        self.assertEqual(exact['used']['work'],13)
        self.assertEqual(exact['peak'],{'objects':6,'scalar':3})
        self.invalid_before_open([final(2,2),hold('a',2,0),hold('b',1,0),DONE])

    def test_released_handle_and_slots_do_not_return_cleanup_allocation(self):
        valid=[final(2,2),hold('a',1,1),release('a'),hold('b',1,1),DONE]
        value=Ledger(CAPS).run(valid)
        self.assertEqual(value['state'],'completed')
        self.assertEqual(value['used']['work'],12)
        self.assertEqual(value['peak'],{'objects':4,'scalar':4})
        self.assertEqual((value['newHandles'],value['newSlots']),(2,2))
        self.invalid_before_open([final(1,2),hold('a'),release('a'),hold('b'),DONE])
        self.invalid_before_open([final(2,1),hold('a'),release('a'),hold('b'),DONE])
        self.invalid_before_open([final(2,2),hold('a'),release('a'),hold('a')|{'id':'a-again'},DONE])
        self.invalid_before_open(valid[:-1]+[release('b'),hold('c'),DONE])

    def test_block_temporary_live_whole_vector_prepaid(self):
        block={'id':'opaque','kind':'block','proof':'independent 7/5/2 plus temporary2/5',
               'charges':{'work':7,'scan_copy':5,'hash_bytes':2},
               'live':{'objects':2,'scalar':5}}
        program=[CONTROL,final(1,2),block,DONE]
        exact=Ledger(CAPS|{'objects':69,'scalar':8,'work':18}).run(program)
        self.assertEqual(exact['state'],'completed')
        self.assertEqual(exact['peak'],{'objects':69,'scalar':8})
        self.assertEqual((exact['used']['work'],exact['used']['scan_copy'],exact['used']['hash_bytes']),(18,11,6))
        self.assertEqual((exact['newHandles'],exact['newSlots']),(1,2))
        short=Ledger(CAPS|{'objects':68,'scalar':8,'work':18}).run(program)
        self.assertEqual((short['state'],short['first'],short['domain']),('failed','opaque','objects'))
        self.assertEqual((short['used']['work'],short['used']['scan_copy'],short['used']['hash_bytes']),(11,6,4))
        self.assertEqual(short['peak'],{'objects':67,'scalar':3})
        self.assertEqual(short['live'],{'objects':0,'scalar':0})
        self.invalid_before_open([final(0,0),block,DONE])

    def test_block_retained_overlaps_temporary_and_never_aliases_control(self):
        block={'id':'opaque','kind':'block','proof':'literal cumulative and temporary/output overlap',
               'charges':{'work':7,'scan_copy':5,'hash_bytes':2},
               'live':{'objects':2,'scalar':5},
               'retained':{'handle':'returned','objects':1,'scalar':2}}
        program=[final(2,3),block,DONE]
        value=Ledger(CAPS|{'work':20,'objects':6,'scalar':10}).run(program)
        self.assertEqual(value['state'],'completed')
        self.assertEqual(value['peak'],{'objects':6,'scalar':10})
        self.assertEqual(value['used']['work'],20)
        self.assertEqual((value['newHandles'],value['newSlots']),(2,3))
        for cap,domain in (({'objects':5},'objects'),({'scalar':9},'scalar'),({'work':19},'work')):
            with self.subTest(cap=cap):
                result=Ledger(CAPS|cap).run(program)
                self.assertEqual(result['domain'],domain)
                self.assertEqual((result['used']['work'],result['used']['scan_copy'],result['used']['hash_bytes']),(13,6,4))
                self.assertEqual(result['peak'],{'objects':3,'scalar':3})
        self.invalid_before_open([final(2,2),block,DONE])
        bad=block|{'retained':{'handle':'control','objects':1,'scalar':2}}
        self.invalid_before_open([final(2,3),bad,DONE])
        self.invalid_before_open([final(2,3),block,release('returned'),hold('next'),DONE])

    def test_failure_reuse_rejected_with_paid_costs_intact(self):
        ledger=Ledger(CAPS|{'objects':67})
        program=[CONTROL,final(1,1),hold('x'),DONE]
        result=ledger.run(program)
        with self.assertRaises(ValueError):ledger.run(program)
        self.assertEqual(result['used']['work'],10)
        self.assertEqual(ledger.used['work'],10)
        self.assertEqual(ledger.state,'failed')
        self.assertEqual(ledger.held,{})


if __name__=='__main__':
    unittest.main(verbosity=2)
