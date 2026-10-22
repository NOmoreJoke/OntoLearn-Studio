"""Independent exact rational IEEE boundary selections, no host float."""
from fractions import Fraction
from pathlib import Path
import json
import sys

HERE=Path(__file__).parent
REF=HERE.parents[2]/'iterations/I05/independent-fee-spec/charge-reference-v2'
sys.path.insert(0,str(REF))
import reference as r

def decimal(q):
    n,d=q.numerator,q.denominator
    assert d&(d-1)==0
    k=d.bit_length()-1;digits=str(abs(n)*5**k).rjust(k+1,'0')
    return ('-' if n<0 else '')+(digits[:-k]+'.'+digits[-k:] if k else digits)
def pow2(k):return Fraction(2**k,1) if k>=0 else Fraction(1,2**(-k))
cases=[]
for dt,p,emin,emax in [('float',24,-126,127),('double',53,-1022,1023)]:
    tiny=pow2(emin-(p-1));half=tiny/2
    cases.extend([(dt,'half-min-subnormal',half,Fraction(0)),
                  (dt,'above-half-min-subnormal',half+pow2(emin-p-30),tiny),
                  (dt,'subnormal-normal-midpoint',pow2(emin)-half,pow2(emin)),
                  (dt,'maxfinite-before-overflow-midpoint',pow2(emax+1)-pow2(emax-p)-1,(2**p-1)*pow2(emax-p+1)),
                  (dt,'overflow-midpoint',pow2(emax+1)-pow2(emax-p),None)])
cases.append(('float','direct-round-double-rounding-counterexample',Fraction(1)+pow2(-24)+pow2(-80),Fraction(1)+pow2(-23)))
rows=[]
for dt,label,raw,expected in cases:
    text=decimal(raw);t=r.Tape('independent IEEE boundary');t.wallet('M',r.caps())
    literal={'kind':'literal','lexical_form':text,'datatype_iri':r.XSD+dt,'language_raw':None,'source':None}
    error=None;got=None
    try:
        result=r.numeric(literal,t,'M');got=Fraction(result['numerator'],result['denominator'])
    except ValueError as e:error=str(e)
    passed=(got==expected and error is None) if expected is not None else error is not None and 'nonfinite' in error
    rows.append({'datatype':dt,'case':label,'lexical':text,'expected':None if expected is None else [expected.numerator,expected.denominator],
                 'actual':None if got is None else [got.numerator,got.denominator],'error':error,'passed':passed})
assert all(x['passed'] for x in rows),rows
(HERE/'independent-r2-numeric-boundaries.json').write_text(json.dumps({'cases':rows,'allPassed':True},ensure_ascii=False,indent=2)+'\n')
print('11 independent exact IEEE underflow/subnormal/normal/overflow/direct-round boundaries: PASS')
