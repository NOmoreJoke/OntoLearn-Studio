"""Docs-only fixture assembly; stdlib arithmetic, never product imports/outputs.

Expected relations/roundings are authored constants. exact_decimal only expands
preselected rational inputs; it neither parses nor quantizes a supplied literal.
This is not a product test or a second general-purpose numeric comparator.
"""

from fractions import Fraction as F
from pathlib import Path
import json

OUT = Path(__file__).parent
X = "http://www.w3.org/2001/XMLSchema#"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
OPS = ["eq", "ne", "lt", "le", "gt", "ge"]
TRUTHS = {
    "less": [False, True, True, True, False, False],
    "equal": [True, False, False, True, False, True],
    "greater": [False, True, False, False, True, True],
}
E3 = "RULE_COMPARISON_TYPE_MISMATCH"


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def number(value, negative_zero=False):
    value = F(value)
    return {"numerator": str(value.numerator), "denominator": str(value.denominator),
            "negative_zero": negative_zero}


def term(text, datatype="string", language=None, iri=False):
    if iri:
        return {"kind": "iri", "lexical_form": text}
    t = {"kind": "literal", "lexical_form": text,
         "datatype_iri": RDF + "langString" if language else X + datatype}
    if language:
        t["language_raw"] = language
    return t


def exact_decimal(value):
    sign = "-" if value < 0 else ""
    value = abs(F(value))
    d, a, b = value.denominator, 0, 0
    while d % 2 == 0:
        d //= 2
        a += 1
    while d % 5 == 0:
        d //= 5
        b += 1
    assert d == 1
    k = max(a, b)
    c = value.numerator * 2 ** (k - a) * 5 ** (k - b)
    whole, fraction = divmod(c, 10 ** k)
    return sign + str(whole) + ("." + str(fraction).rjust(k, "0") if k else "")


representatives = {
    "N": term("2", "integer"), "S": term("a"),
    "L": term("a", language="EN-us"), "I": term("urn:m1:i", iri=True),
    "B": term("true", "boolean"), "Dz": term("0000-03-01Z", "date"),
    "Dl": term("0000-03-01", "date"),
    "Tz": term("0000-03-01T00:00:00Z", "dateTime"),
    "Tl": term("0000-03-01T00:00:00", "dateTime"),
}
cells = []
for left in representatives:
    for right in representatives:
        for i, op in enumerate(OPS):
            valid = left == right and (left not in ["I", "B"] or i < 2)
            cells.append({"id": left + "/" + right + "/" + op,
                          "leftDomain": left, "rightDomain": right, "operator": op,
                          "expected": {"boolean": TRUTHS["equal"][i]} if valid else {"reason": E3}})
types = ["integer", "int", "nonNegativeInteger", "decimal", "float", "double"]
numeric_cells = []
for left in types:
    for right in types:
        for relation, a in [("less", "1"), ("equal", "2"), ("greater", "3")]:
            for i, op in enumerate(OPS):
                numeric_cells.append({"id": left + "/" + right + "/" + relation + "/" + op,
                                      "left": term(a, left), "right": term("2", right),
                                      "leftNumber": number(int(a)), "rightNumber": number(2),
                                      "operator": op, "expectedBoolean": TRUTHS[relation][i]})
save("domain-operator-goldens.json", {
    "status": "independent expected only; zero product executions",
    "method": "Explicit profile cell policy and three authored truth rows, no comparator invocation",
    "operatorOrder": OPS, "representatives": representatives, "nineDomainCells": cells,
    "numericDatatypes": types, "numericPairRelationCells": numeric_cells,
    "coverage": {"nineDomainSlots": 486, "numericOrderedPairs": 36,
                 "numericOperatorSlots": 216, "numericThreeRelationInstances": 648},
    "notClaimed": "Finite values do not exhaust all lexical/rational inputs; none is a runtime pass count",
})

vectors = []


def nv(id, datatype, mathematical_input, expected=None, negative_zero=False, lexical=None,
       reason=None, proof=""):
    r = {"id": id, "input": term(lexical if lexical is not None else exact_decimal(F(mathematical_input)), datatype),
         "exactDecimalInput": number(F(mathematical_input)), "derivation": proof}
    r["expected"] = {"reason": reason} if reason else {"Number": number(expected, negative_zero)}
    vectors.append(r)


for dtype in types:
    nv("two-" + dtype, dtype, 2, 2,
       lexical={"integer": "02", "int": "+2", "nonNegativeInteger": "2",
                "decimal": "2.0", "float": "2e0", "double": "+2E0"}[dtype],
       proof="All six actual values are exactly 2; original datatype/lexical remain distinct RDF terms")
for dtype, val in [("decimal", F(1, 10)), ("float", F(13421773, 134217728)),
                   ("double", F(3602879701896397, 36028797018963968))]:
    nv("point-one-" + dtype, dtype, F(1, 10), val, lexical="0.1",
       proof="decimal is 1/10; nearest binary significands independently fixed; float > double > decimal")
nv("large-int-32", "integer", 16777217, 16777217)
nv("large-float-32", "float", 16777217, 16777216, proof="At 2^24 step=2; odd midpoint takes even lower significand")
nv("large-int-64", "integer", 9007199254740993, 9007199254740993)
nv("large-double-64", "double", 9007199254740993, 9007199254740992,
   proof="At 2^53 step=2; odd midpoint takes even lower significand")
for dtype in ["integer", "decimal", "float", "double"]:
    nv("negative-zero-" + dtype, dtype, 0, 0, negative_zero=dtype in ["float", "double"], lexical="-0",
       proof="Only binary float/double retain negative_zero; comparisons still use equal zero row")
for dtype, precision, emin, emax, sub in [("float", 24, -126, 127, 149), ("double", 53, -1022, 1023, 1074)]:
    q = F(1, 2 ** sub)
    half_ulp = F(1, 2 ** precision)
    nv(dtype + "-tie-low", dtype, 1 + half_ulp, 1, proof="Exact midpoint; lower significand even")
    nv(dtype + "-tie-high", dtype, 1 + 3 * half_ulp, 1 + 4 * half_ulp,
       proof="Exact midpoint; upper significand even")
    for suffix, value, expected, nz, proof in [
        ("half-subnormal", q / 2, 0, False, "Tie between 0 and q, even 0"),
        ("negative-half-subnormal", -q / 2, 0, True, "Same tie; negative sign retained at zero"),
        ("min-subnormal", q, q, False, "Exactly one least subnormal quantum"),
        ("three-half-subnormal", 3 * q / 2, 2 * q, False, "Tie between 1q and 2q; even 2q"),
        ("subnormal-normal-tie", F(1, 2 ** -emin) - q / 2, F(1, 2 ** -emin), False,
         "Last subnormal odd, minimum normal even")]:
        nv(dtype + "-" + suffix, dtype, value, expected, nz, proof=proof)
    maximum = (2 ** precision - 1) * 2 ** (emax - precision + 1)
    midpoint = 2 ** (emax + 1) - 2 ** (emax - precision)
    nv(dtype + "-max-finite", dtype, maximum, maximum, proof="(2^p-1)*2^(emax-p+1)")
    nv(dtype + "-below-overflow-midpoint", dtype, midpoint - 1, maximum,
       proof="Exactly one integer below overflow tie, rounds down to max finite")
    nv(dtype + "-overflow-midpoint", dtype, midpoint, reason="UNSUPPORTED_NONFINITE_LITERAL",
       proof="Tie rounds even into 2^(emax+1), unsupported infinity; legal lexical, no clamp")
nv("float-double-rounding-counterexample", "float", 1 + F(1, 2 ** 24) + F(1, 2 ** 80),
   F(8388609, 8388608), proof="2^-80 above binary32 midpoint; direct32 up. Via64 loses perturbation and incorrectly rounds32 to1")
save("number-goldens.json", {"status": "independent exact values, not observed product values",
    "record": "Number(numerator:int,denominator:int,negative_zero:bool); JSON integer strings are golden storage only, not public codec",
    "vectors": vectors, "mixedRelations": [
        {"leftId": "point-one-float", "rightId": "point-one-double", "relation": "greater", "sixBooleans": TRUTHS["greater"]},
        {"leftId": "point-one-double", "rightId": "point-one-decimal", "relation": "greater", "sixBooleans": TRUTHS["greater"], "difference": number(F(1, 180143985094819840))},
        {"leftId": "point-one-float", "rightId": "point-one-decimal", "relation": "greater", "sixBooleans": TRUTHS["greater"], "difference": number(F(1, 671088640))},
        {"leftId": "large-int-32", "rightId": "large-float-32", "relation": "greater", "sixBooleans": TRUTHS["greater"]},
        {"leftId": "large-int-64", "rightId": "large-double-64", "relation": "greater", "sixBooleans": TRUTHS["greater"]}],
    "zeroComparison": {"allSignedZeros": TRUTHS["equal"], "retainOriginalTerm": True}})

calendar = []
for id, dtype, lexical, day, seconds, explicit in [
    ("Dz", "date", "0000-03-01Z", 0, F(0), True),
    ("Dl", "date", "0000-03-01", 0, F(0), False),
    ("Tz", "dateTime", "0000-03-01T00:00:00Z", 0, F(0), True),
    ("Tl", "dateTime", "0000-03-01T00:00:00", 0, F(0), False),
    ("date-plus14", "date", "0000-03-01+14:00", -1, F(36000), True),
    ("date-minus10", "date", "0000-02-29-10:00", -1, F(36000), True),
    ("datetime-plus1", "dateTime", "0000-03-01T00:30:00+01:00", -1, F(84600), True),
    ("datetime-z-equivalent", "dateTime", "0000-02-29T23:30:00Z", -1, F(84600), True),
    ("24h", "dateTime", "0000-02-29T24:00:00.000Z", 0, F(0), True),
    ("fraction", "dateTime", "0000-03-01T00:00:00.1234567890123456789", 0, F(1234567890123456789, 10 ** 19), False),
    ("negative-zero-year", "date", "-0000-03-01", 0, F(0), False),
    ("negative-year", "date", "-0001-03-01Z", -366, F(0), True),
    ("400year", "date", "0400-03-01", 146097, F(0), False),
    ("400leap", "date", "0400-02-29", 146096, F(0), False),
    ("minus-zero-offset", "dateTime", "0000-03-01T00:00:00-00:00", 0, F(0), True),
]:
    calendar.append({"id": id, "input": term(lexical, dtype),
                     "expectedDomain": ("T" if dtype == "dateTime" else "D") + ("z" if explicit else "l"),
                     "expectedCalendar": {"day": day, "second": number(seconds), "explicit_offset": explicit, "is_datetime": dtype == "dateTime"}})
save("calendar-goldens.json", {"status": "independent expected only", "epoch": "0000-03-01",
    "derivation": "Jan-origin days=365*y+(y+3)//4-(y+99)//100+(y+399)//400+priorMonthDays+d-1-60; subtract offset seconds, floor into day. Product March/era formula never called.",
    "vectors": calendar, "equalPairs": [["date-plus14", "date-minus10"], ["datetime-plus1", "datetime-z-equivalent"], ["Tz", "24h"], ["Tz", "minus-zero-offset"], ["Dl", "negative-zero-year"]],
    "crossDomainEvenIfSameDaySecond": "All six operators fail RULE_COMPARISON_TYPE_MISMATCH; no implicit timezone/date cast"})

semantics = [
    {"id": "codepoint-order", "left": term("\U00010000"), "right": term("\ue000"), "relation": "greater", "proof": "65536 > 57344, not UTF16 unit order"},
    {"id": "no-nfc", "left": term("é"), "right": term("e\u0301"), "relation": "greater", "proof": "First codepoint233 >101; no normalization"},
    {"id": "language-ascii-lower", "left": term("a", language="EN-us"), "right": term("a", language="en-US"), "relation": "equal", "language": "en-us"},
    {"id": "language-no-fallback", "left": term("a", language="en-US"), "right": term("a", language="en"), "allReasons": E3},
    {"id": "iri-spelling", "left": term("HTTP://EXAMPLE/a", iri=True), "right": term("http://example/a", iri=True), "eq": False, "ne": True, "orderedReasons": E3},
    {"id": "iri-unicode-nbsp", "left": term("urn:m1:a\u00a0b", iri=True), "right": term("urn:m1:ab", iri=True), "eq": False, "ne": True, "orderedReasons": E3},
    {"id": "boolean-alias", "left": term("true", "boolean"), "right": term("1", "boolean"), "eq": True, "ne": False, "orderedReasons": E3, "sameRdfTerm": False},
    {"id": "integer-term-vs-value", "left": term("01", "integer"), "right": term("1", "integer"), "relation": "equal", "sameRdfTerm": False},
    {"id": "simple-explicit-string", "left": {"kind": "literal", "lexical_form": "a"}, "right": term("a"), "relation": "equal", "sameRdfTerm": True},
]
for s in semantics:
    if "relation" in s:
        s["sixBooleans"] = TRUTHS[s["relation"]]
errors = []
for dtype, lexicals in [("integer", [" 1", "١", "1_0"]), ("int", ["2147483648"]),
                        ("nonNegativeInteger", ["-1"]), ("decimal", ["1e0"]),
                        ("boolean", ["True", "+1", "01"]),
                        ("float", ["+NaN", "inf"]),
                        ("date", ["0100-02-29", "0000-03-01+14:01"]),
                        ("dateTime", ["0000-03-01T24:00:00.1Z", "0000-03-01T00:00:60Z"]),
                        ("string", ["\u0000", "\ufffe", "\uffff"])]:
    for lexical in lexicals:
        errors.append({"input": term(lexical, dtype), "reason": "INVALID_LITERAL_LEXICAL"})
for dtype in ["float", "double"]:
    for lexical in ["NaN", "INF", "+INF", "-INF"]:
        errors.append({"input": term(lexical, dtype), "reason": "UNSUPPORTED_NONFINITE_LITERAL"})
errors += [{"input": {"kind": "literal", "lexical_form": "x", "datatype_iri": "urn:m1:unknown"}, "reason": "UNSUPPORTED_LITERAL_DATATYPE"},
           {"input": {"kind": "literal", "lexical_form": "a", "datatype_iri": X + "string", "language_raw": "en"}, "reason": "INVALID_RULE"},
           {"input": term("relative", iri=True), "reason": "INVALID_RULE"},
           {"operator": "=", "reason": "INVALID_RULE"}, {"operator": "EQ", "reason": "INVALID_RULE"},
           {"operator": 1, "reason": "INTERNAL_ERROR"}]
for i, error in enumerate(errors):
    error["id"] = "error/" + str(i)
save("term-error-goldens.json", {"status": "expected only; reasons private, not new public wire codes", "semantics": semantics,
    "lexicalAndSupportErrors": errors, "precedence": "Validate lexical/support/resource before type classification. Nonfinite is not false. Resource maps existing adapter only.",
    "languageBoundary": {"acceptedAbnfOnly": ["x-private", "i-klingon", "en-1901-1901", "en-a-foo-a-bar"], "notRegistryValidated": True},
    "stringVsLanguage": "S XML1.1 Char; L Unicode scalars, do not add S XML Char restriction to L"})

# Independent source inputs are assembled from the same authored operand
# constants, never read back from a golden file or from a product execution.
# Expected fields stay in the separate files above and are not producer input.
save("math-operand-inputs.json", {
    "status": "new independently authored source operands only; no expected mathematical values/results/reasons",
    "caseKey": "family + id; golden file families match by id, never by actual result",
    "domainComparisonCases": [
        {"id": c["id"], "left": representatives[c["leftDomain"]],
         "right": representatives[c["rightDomain"]], "operator": c["operator"]}
        for c in cells
    ],
    "numericComparisonCases": [
        {"id": c["id"], "left": c["left"], "right": c["right"], "operator": c["operator"]}
        for c in numeric_cells
    ],
    "numberDecodeCases": [{"id": c["id"], "input": c["input"]} for c in vectors],
    "mixedNumericComparisonCases": [
        {"id": a + "/" + b + "/" + op,
         "leftNumberCaseId": a, "rightNumberCaseId": b,
         "left": next(v["input"] for v in vectors if v["id"] == a),
         "right": next(v["input"] for v in vectors if v["id"] == b), "operator": op}
        for a, b in [("point-one-float", "point-one-double"),
                     ("point-one-double", "point-one-decimal"),
                     ("point-one-float", "point-one-decimal"),
                     ("large-int-32", "large-float-32"),
                     ("large-int-64", "large-double-64")]
        for op in OPS
    ],
    "signedZeroComparisonCases": [
        {"id": dtype + "/signed-zero/" + op,
         "left": term("-0", dtype), "right": term("0", dtype), "operator": op}
        for dtype in ["integer", "decimal", "float", "double"] for op in OPS
    ],
    "calendarDecodeCases": [{"id": c["id"], "input": c["input"]} for c in calendar],
    "termComparisonCases": [
        {"id": c["id"] + "/" + op, "termCaseId": c["id"],
         "left": c["left"], "right": c["right"], "operator": op}
        for c in semantics for op in OPS
    ],
    "errorOperandCases": [
        dict({"id": c["id"]}, **(
            {"input": c["input"]} if "input" in c else
            {"operator": c["operator"], "left": term("2", "integer"), "right": term("2", "integer")}
        )) for i, c in enumerate(errors)
    ],
    "languageAbnfInputs": [
        {"id": "language/" + tag, "input": term("a", language=tag)}
        for tag in ["x-private", "i-klingon", "en-1901-1901", "en-a-foo-a-bar"]
    ],
})

# author-method.json is a separately maintained review/failure ledger, never overwritten here.
