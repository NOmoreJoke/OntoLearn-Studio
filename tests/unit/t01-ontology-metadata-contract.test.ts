import { execFileSync } from 'node:child_process'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import type { OntologyEntityMetadataDTO as Metadata } from '@ontolearn/contracts'
import { validateV2 } from '../../packages/contracts/src/v2'

const iri = 'urn:equipment:Equipment'
function base(): Metadata {
  return {
    entityMetadataVersion: 1,
    entities: {
      [iri]: {
        identifier: 'Equipment',
        labels: [
          ['设备', 'zh'],
          ['Equipment', 'en'],
        ],
        definitions: [['可维护的设备', 'zh']],
        synonyms: ['资产'],
        examples: ['泵站 A'],
      },
    },
  }
}
const cases: Array<{ name: string; value: unknown; expected: boolean }> = []
function vector(name: string, expected: boolean, change: (value: Metadata) => void) {
  const value = base()
  change(value)
  cases.push({ name, value, expected })
}
vector('complete metadata', true, () => {})
vector('numeric first identifier', true, (v) => {
  v.entities[iri].identifier = '1_Equipment-2'
})
vector('underscore first identifier', true, (v) => {
  v.entities[iri].identifier = '_Equipment'
})
vector('identifier has no separate 128 limit', true, (v) => {
  v.entities[iri].identifier = 'A'.repeat(129)
})
vector('identifier dot', false, (v) => {
  v.entities[iri].identifier = 'Equipment.bad'
})
vector('identifier final newline', false, (v) => {
  v.entities[iri].identifier = 'Equipment\n'
})
vector('same language multiple values', true, (v) => {
  v.entities[iri].labels.push(['运维设备', 'zh'])
})
vector('duplicate exact pair', false, (v) => {
  v.entities[iri].labels.push(['设备', 'zh'])
})
vector('uppercase language', false, (v) => {
  v.entities[iri].labels[0][1] = 'zh-CN'
})
vector('language final newline', false, (v) => {
  v.entities[iri].labels[0][1] = 'zh\n'
})
vector('lowercase subtag', true, (v) => {
  v.entities[iri].labels[0][1] = 'zh-cn'
})
vector('empty language', true, (v) => {
  v.entities[iri].labels[0][1] = ''
})
vector('empty collections', true, (v) => {
  Object.assign(v.entities[iri], { labels: [], definitions: [], synonyms: [], examples: [] })
})
vector('Python control whitespace only', false, (v) => {
  v.entities[iri].synonyms = ['\u001c']
})
vector('FEFF is preserved text', true, (v) => {
  v.entities[iri].synonyms = ['\ufeff']
})
vector('text whitespace is preserved', true, (v) => {
  v.entities[iri].synonyms = [' 设备 ']
})
vector('no new NUL ban for non-RDF text', true, (v) => {
  v.entities[iri].examples = ['\u0000']
})
vector('duplicate synonyms', false, (v) => {
  v.entities[iri].synonyms.push('资产')
})
vector('duplicate examples', false, (v) => {
  v.entities[iri].examples.push('泵站 A')
})
vector('16000 Unicode codepoints', true, (v) => {
  v.entities[iri].labels = [['𠮷'.repeat(16000), 'zh']]
})
vector('16001 Unicode codepoints', false, (v) => {
  v.entities[iri].labels = [['𠮷'.repeat(16001), 'zh']]
})
vector('surrogate', false, (v) => {
  v.entities[iri].examples = ['\ud800']
})
vector('two IRIs may share identifier', true, (v) => {
  v.entities['urn:equipment:Other'] = structuredClone(v.entities[iri])
})
vector('relative IRI key', false, (v) => {
  v.entities.relative = v.entities[iri]
})
vector('IRI whitespace', false, (v) => {
  v.entities['urn:equipment:bad\u001c'] = v.entities[iri]
})
cases.push({
  name: 'bool version',
  value: { ...base(), entityMetadataVersion: true },
  expected: false,
})
cases.push({ name: 'extra key', value: { ...base(), extra: 1 }, expected: false })
cases.push({
  name: 'missing entity field',
  value: { entityMetadataVersion: 1, entities: { [iri]: { identifier: 'Equipment' } } },
  expected: false,
})

function wrappers(value: unknown): Array<[string, unknown]> {
  const ontology = { triples: [], entityMetadata: value }
  const definition = { layer: 'ontology', id: 'equipment', value: ontology }
  const plan = { definitions: [definition] }
  const params = {
    projectId: '00000000-0000-4000-8000-000000000001',
    baseRevision: 0,
    intent: 'change',
    plan,
  }
  return [
    ['changeSetEntityMetadata', value],
    ['changeSetOntologyValue', ontology],
    ['changeSetDefinition', definition],
    ['changeSetPlan', plan],
    ['params_changeset.preview', params],
    [
      'request3',
      {
        kind: 'request',
        protocolVersion: 3,
        id: '00000000-0000-4000-8000-000000000002',
        engineSessionId: '00000000-0000-4000-8000-000000000003',
        method: 'changeset.preview',
        params,
      },
    ],
  ]
}
describe('canonical M input fields through the existing ChangeSet contract', () => {
  it.each(cases)(
    '$name has the same result at every containing boundary',
    ({ value, expected }) => {
      for (const [name, input] of wrappers(value))
        expect(validateV2(name, input), name).toBe(expected)
    },
  )
  it('keeps an absent metadata namespace legal and rejects public opaque injection', () => {
    expect(validateV2('changeSetOntologyValue', { triples: [] })).toBe(true)
    expect(validateV2('changeSetOntologyValue', { triples: [], legacyOpaque: {} })).toBe(false)
  })
  it('checks all literal vectors with the actual Python contract', () => {
    const rows = cases.flatMap((c) =>
      wrappers(c.value).map(([name, value]) => ({ name, value, expected: c.expected })),
    )
    const script = `import importlib.util,json,sys
from pathlib import Path
path=Path.cwd()/'packages/contracts/python/contract_v2.py'
spec=importlib.util.spec_from_file_location('metadata_contract',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
print(json.dumps([module.validate(row['name'],row['value']) for row in json.load(sys.stdin)]))`
    const result = JSON.parse(
      execFileSync('python', ['-I', '-B', '-c', script], {
        cwd: resolve('.'),
        input: JSON.stringify(rows),
        encoding: 'utf8',
        timeout: 30000,
        maxBuffer: 1024 * 1024,
      }),
    )
    expect(result).toEqual(rows.map((r) => r.expected))
  })
})
