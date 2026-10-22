"""Literal independent encoding/math expectations, not product fixtures."""
import unittest
import reference as r

class PureReferenceTests(unittest.TestCase):
    def tape(self):
        t=r.Tape('independent hand selection');t.wallet('M',r.caps());return t
    def literal(self,text,dt):return {'kind':'literal','lexical_form':text,'datatype_iri':r.XSD+dt,'language_raw':None,'source':None}
    def test_fee_codec_literal_hex_and_shape(self):
        for value,golden in [(None,'4e'),('é','5300000002c3a9'),(-1,'49000000042d307831'),([True,None],'4100000002544e'),({'z':0},'520000000153000000017a4900000003307830')]:
            with self.subTest(value=value):self.assertEqual(r.encode(value).hex(),golden)
        self.assertEqual(r.shape({'z':0}),(3,2))
        self.assertNotEqual(r.encode(None),r.encode(''))
        self.assertNotEqual(r.encode(True),r.encode(1))
    def test_key_57_and_alias_raw_distinctions(self):
        term=r.term('<urn:x>');key=r.complete_key(term)
        self.assertEqual(len(key),57)
        self.assertEqual(key[:9],b'I05RTK1\0\0')
        self.assertEqual(key[9:17],b'\1\0\0\0\3iri')
        self.assertEqual(key[17:27],b'\1\0\0\0\5urn:x')
        self.assertEqual(key[27:],b'\0'*30)
        source={k:None for k in ('reference','digest','revision','text')}
        self.assertNotEqual(key,r.complete_key(term|{'source':source}))
        self.assertNotEqual(r.complete_key(term|{'source':source}),r.complete_key(term|{'source':source|{'text':''}}))
        en=self.literal('x','string')|{'language_raw':'EN'};lower=en|{'language_raw':'en'}
        self.assertEqual(r.identity(en),r.identity(lower))
        self.assertNotEqual(r.complete_key(en),r.complete_key(lower))
    def test_integer_123_hand_13_and_decimal_one_tenth_hand_12(self):
        t=self.tape();self.assertEqual(r.numeric(self.literal('123','integer'),t,'M'),{'numerator':123,'denominator':1,'negative_zero':False})
        # digit Horner6 + exponent Horner2 + square1 + finalmul1 + Euclid1 + reduce2.
        self.assertEqual(t.used['M']['work'],13)
        t=self.tape();self.assertEqual(r.numeric(self.literal('0.1','decimal'),t,'M'),{'numerator':1,'denominator':10,'negative_zero':False})
        # two digits4 + exponent2 + ten-power2 + Euclid2 + reduction2.
        self.assertEqual(t.used['M']['work'],12)
    def test_ieee_independent_exact_ratios_and_ties(self):
        for text,dt,n,d in [('0.1','float',13421773,134217728),('0.1','double',3602879701896397,36028797018963968),('16777217','float',16777216,1),('9007199254740993','double',9007199254740992,1)]:
            with self.subTest(text=text,dt=dt):
                v=r.numeric(self.literal(text,dt),self.tape(),'M');self.assertEqual((v['numerator'],v['denominator']),(n,d))
        self.assertTrue(r.numeric(self.literal('-0','double'),self.tape(),'M')['negative_zero'])
    def test_limb_bound_precedes_hold_or_work_mutation(self):
        t=self.tape()
        with self.assertRaises(ValueError):t.arithmetic('M','mul',1<<32767,2)
        self.assertEqual((t.events,t.handles,t.used['M']['work']),([],{},0))
        with self.assertRaises(ValueError):t.shift('M',1,32768)
        self.assertEqual(t.events,[])
    def test_false_does_not_erase_later_operand_type_error(self):
        t=self.tape();one=r.parse_math(self.literal('1','integer'),t,'M');two=r.parse_math(self.literal('2','integer'),t,'M')
        self.assertFalse(r.compare_math(one,'gt',two,t,'M'))
        text=r.parse_math(self.literal('x','string'),t,'M')
        with self.assertRaises(ValueError):r.compare_math(one,'ne',text,t,'M')
        self.assertEqual(sum(e['action']=='comparison occurrence' for e in t.events),2)
        self.assertEqual(t.used['M']['head_occurrences'],0)
    def test_allocator_three_rules_full_literal_remainder_and_dummy(self):
        children=r.allocation([{'rule_id':'z'},{'rule_id':'a'},{'rule_id':'m'}],['a'])
        self.assertEqual([(c['rule_id'],c['ordinal'],c['disabled']) for c in children],[('a',1,True),('m',2,False),('z',0,False)])
        self.assertEqual([c['limits']['work'] for c in children],[5592406,5592405,5592405])
        self.assertEqual([c['limits']['input_bytes'] for c in children],[87382,87381,87381])
        self.assertTrue(all(len(c['limits'])==17 for c in children))
        dummy=r.allocation([],[])[0];self.assertEqual((dummy['rule_id'],dummy['ordinal'],dummy['disabled']),(None,None,False))
        self.assertEqual(dummy['limits']['work'],16777216)
    def test_q6_calendar_literal_day_second_and_timezone_domains(self):
        for text,dt,day,num,den in [('0000-03-01','date',0,0,1),('-0000-03-01','date',0,0,1),('0000-02-29','date',-1,0,1),('-0001-03-01','date',-366,0,1),('0000-12-31T24:00:00.000Z','dateTime',306,0,1),('0000-03-01T00:30:00+01:00','dateTime',-1,84600,1),('0000-03-01T00:00:00.0000001Z','dateTime',0,1,10000000)]:
            with self.subTest(text=text):
                v=r.calendar_math(self.literal(text,dt),self.tape(),'M');self.assertEqual((v['day'],v['second']['numerator'],v['second']['denominator']),(day,num,den))
        for text in ('00000-03-01','+0001-03-01','0000-03-01T24:00:00.1Z','0000-03-01T00:00:60Z','0000-03-01T00:00:00+14:01'):
            with self.subTest(invalid=text):
                with self.assertRaises(ValueError):r.calendar_math(self.literal(text,'dateTime' if 'T' in text else 'date'),self.tape(),'M')
        t=self.tape();local=r.parse_math(self.literal('0000-03-01','date'),t,'M');zone=r.parse_math(self.literal('0000-03-01Z','date'),t,'M')
        self.assertEqual((local['domain'],zone['domain']),('Dl','Dz'))
        with self.assertRaises(ValueError):r.compare_math(local,'ne',zone,t,'M')
    def test_q6_far_exponents_signed_zero_and_strict_integer_zero(self):
        for text,negative in [('1e-100000',False),('-1e-100000',True),('-0e100000',True)]:
            value=r.numeric(self.literal(text,'double'),self.tape(),'M');self.assertEqual(value,{'numerator':0,'denominator':1,'negative_zero':negative})
        for text in ('1e100000','NaN','+INF'):
            with self.assertRaisesRegex(ValueError,'UNSUPPORTED_NONFINITE'):r.numeric(self.literal(text,'float'),self.tape(),'M')
        self.assertFalse(r.numeric(self.literal('-0','integer'),self.tape(),'M')['negative_zero'])
    def test_q6_string_language_and_q2_domains(self):
        for good in ('en-Latn-US','x-a','i-klingon','en-a-xx-a-yy','de-1996-1996','zh-min-nan'):
            self.assertTrue(r.language_wellformed(good),good)
        for bad in ('','en_uk','x','en-','é','en-x'):
            self.assertFalse(r.language_wellformed(bad),bad)
        t=self.tape();a=r.parse_math(self.literal(chr(0x10000),'string'),t,'M');b=r.parse_math(self.literal(chr(0xe000),'string'),t,'M')
        self.assertTrue(r.compare_math(a,'gt',b,t,'M'))
        for text in ('\0',chr(0xfffe),chr(0xffff)):
            with self.assertRaises(ValueError):r.parse_math(self.literal(text,'string'),self.tape(),'M')
        r.parse_math(self.literal('\0','string')|{'datatype_iri':r.RDF+'langString','language_raw':'en'},self.tape(),'M')
        for value in (r.term('<urn:x>'),self.literal('true','boolean')):
            t=self.tape();parsed=r.parse_math(value,t,'M')
            self.assertTrue(r.compare_math(parsed,'eq',parsed,t,'M'))
            with self.assertRaises(ValueError):r.compare_math(parsed,'lt',parsed,t,'M')
    def test_q6_nine_domain_six_operator_literal_matrix(self):
        terms=[self.literal('1','integer'),self.literal('s','string'),self.literal('x','string')|{'datatype_iri':r.RDF+'langString','language_raw':'en'},r.term('<urn:x>'),self.literal('true','boolean'),self.literal('0000-03-01Z','date'),self.literal('0000-03-01','date'),self.literal('0000-03-01T00:00:00Z','dateTime'),self.literal('0000-03-01T00:00:00','dateTime')]
        classes=('N','S','L','I','B','Dz','Dl','Tz','Tl');ops=('eq','ne','lt','le','gt','ge')
        for i,left in enumerate(terms):
            for j,right in enumerate(terms):
                for op in ops:
                    t=self.tape();a=r.parse_math(left,t,'M');b=r.parse_math(right,t,'M')
                    permitted=i==j and (classes[i] not in ('I','B') or op in ('eq','ne'))
                    if permitted:self.assertIs(r.compare_math(a,op,b,t,'M'),{'eq':True,'ne':False,'lt':False,'le':True,'gt':False,'ge':True}[op])
                    else:
                        with self.assertRaises(ValueError):r.compare_math(a,op,b,t,'M')

    def test_q6_six_numeric_pairs_six_ops_three_literal_truths(self):
        names=('integer','int','nonNegativeInteger','decimal','float','double')
        for left_type in names:
            for right_type in names:
                for value in (1,2,3):
                    expected={'eq':value==2,'ne':value!=2,'lt':value<2,'le':value<=2,'gt':value>2,'ge':value>=2}
                    for op in expected:
                        t=self.tape();left=r.parse_math(self.literal(str(value),left_type),t,'M');right=r.parse_math(self.literal('2',right_type),t,'M')
                        self.assertIs(r.compare_math(left,op,right,t,'M'),expected[op])

    def test_source_record_uses_content_and_pointer_not_locator_as_source(self):
        a=r.source_record({'triple':'x','source':{'path':'p'}},'/datasets/x/input/asserted/0')
        self.assertEqual(a['text'],'{"source":{"path":"p"},"triple":"x"}')
        self.assertEqual(a['digest'],r.sha(a['text'].encode()))
        self.assertEqual(a['reference'],'{"datasetField":"/datasets/x/input/asserted/0","feeAssetRef":"0e42a0fe349054a92817cb4d463bccdc15f6c042"}')
        self.assertNotEqual(a['text'],'p')

if __name__=='__main__':unittest.main(verbosity=2)
