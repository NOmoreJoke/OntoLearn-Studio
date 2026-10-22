from pathlib import Path
import subprocess,hashlib,json
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'docs/reviews/I05/independent-fee-spec/author-v2-inputs'
S=[
('q6','9333e69234a6f54a0dfc1485f49d8fdeb4b69cfd','docs/iterations/T05/q6-profile-mechanism-stage-plan.md'),
('parity','ee2b30a2dad35b2d395f9c735aff80371ab41110','docs/iterations/I05/source-package-parity/contract.md'),
('integration','de37ff64fab7f40b69fbf900e4657137ca18ce74','docs/iterations/I05/profile-integration-new-candidate-plan.md'),
('restore','851e6241233d8b7a8f944944207260436b524e9f','docs/iterations/I05/profile-saved-restore-next-plan.md'),
('budget','851e6241233d8b7a8f944944207260436b524e9f','docs/reviews/I05/profile-saved-restore-next-plan/budget-source-preparation.md'),
('census','851e6241233d8b7a8f944944207260436b524e9f','docs/reviews/I05/profile-saved-restore-next-plan/representation-census.md'),
('producer','a3592837d854628948ef4c468b6c839f21763273','docs/iterations/I05/formal-producer-and-selected-integration-plan.md'),
('direct','6891a5842302859a531cf82767c5a482417bc274','docs/reviews/I05/profile-directsteps/inputs/profile-M1-directsteps-consumer-contract.md.raw'),
('dmodel','6891a5842302859a531cf82767c5a482417bc274','docs/reviews/I05/profile-directsteps/inputs/budget-model.json.raw'),
('adoption','6891a5842302859a531cf82767c5a482417bc274','docs/reviews/I05/profile-directsteps/inputs/I05-profile-directsteps-first-fixed-inputs.json.raw'),
('gaps','3d8f4ee912f41bd03388322d29a9bfc0e7defe85','tests/fixtures/quality/i05-source-package-oracle/budget-gaps.json'),
('policies','3d8f4ee912f41bd03388322d29a9bfc0e7defe85','docs/iterations/T05/source-package-oracle/field-policies.md'),
('readme','3d8f4ee912f41bd03388322d29a9bfc0e7defe85','docs/reviews/T05/source-package-oracle/README.md'),
('sources','3d8f4ee912f41bd03388322d29a9bfc0e7defe85','tests/fixtures/quality/i05-source-package-oracle/sources.json'),
('coverage','3d8f4ee912f41bd03388322d29a9bfc0e7defe85','tests/fixtures/quality/i05-source-package-oracle/coverage.json'),
('oracle','3d8f4ee912f41bd03388322d29a9bfc0e7defe85','tests/fixtures/quality/i05-source-package-oracle/oracle.json'),
('oracle-schema','3d8f4ee912f41bd03388322d29a9bfc0e7defe85','tests/fixtures/quality/i05-source-package-oracle/schema.json'),
('inputs','0e42a0fe349054a92817cb4d463bccdc15f6c042','packages/engine/src/ontolearn_engine/probe_inputs/i05-source-package-parity-inputs.json'),
('input-manifest','0e42a0fe349054a92817cb4d463bccdc15f6c042','packages/engine/src/ontolearn_engine/probe_inputs/i05-source-package-parity-manifest.json')]
rows=[]
for name,ref,path in S:
 b=subprocess.check_output(['git','show',f'{ref}:{path}'],cwd=ROOT)
 fn=name+('.json' if path.endswith(('.json','.json.raw')) else '.md')
 (OUT/fn).write_bytes(b)
 rows.append(dict(name=name,ref=ref,path=path,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),lines=len(b.splitlines()),copy=str((OUT/fn).relative_to(ROOT))))
for local,expected in [('AGENTS.md','78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759'),('docs/reviews/I05/independent-fee-spec/local-proof-excerpts.json','7f66f8cdddf35462b55fb226f7ed76fe362ec3c490af3cc461f1aa6b20acf713')]:
 b=(ROOT/local).read_bytes(); h=hashlib.sha256(b).hexdigest(); assert h==expected
 rows.append(dict(name=local,path=local,bytes=len(b),sha256=h,lines=len(b.splitlines())))
assert next(r for r in rows if r['name']=='gaps')['sha256']=='4a0e72d103a156117e461810d1e0f27a4e96c8f69a56d405111cab34b99300e6'
api=Path('/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/I05-canonical-profile-api-defaults-reference.json')
b=api.read_bytes()
(OUT/'api-defaults-reference.json').write_bytes(b)
rows.append(dict(name='api-defaults-reference',path=str(api),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),lines=len(b.splitlines()),copy=str((OUT/'api-defaults-reference.json').relative_to(ROOT)),permission='root explicitly authorized declaration-only AST excerpt; no actual invocation proof'))
(OUT.parent/'input-manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(rows,ensure_ascii=False,indent=2))
