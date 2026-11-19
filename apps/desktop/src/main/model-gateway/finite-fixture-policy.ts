import type { StoredFieldModel } from './stored-field-projector'

// A fixed synthetic producer policy for the existing main-only trusted launch fixture.
// It is never selected by a result tag, renderer data or a normal product setting.
export function finiteFixturePolicy(dependencyLockHash: string): StoredFieldModel {
  return {
    id: 'i06-finite-probe',
    version: 'v1',
    producerCapability: 'test.read',
    definitionId: 'i06-material-probe',
    kind: 'test',
    tag: 'I06_FINITE_FIELDS',
    implementation: {
      executionSemanticsVersion: 'i04-infrastructure-v1',
      engineVersion: '0.1.0',
      dependencyLockHash,
    },
    fields: [
      {
        key: 'public',
        label: 'Public label',
        index: 1,
        type: 'string',
        nullable: false,
        dependsOn: [],
      },
      {
        key: 'private',
        label: 'PRIVATE_LABEL_SENTINEL',
        index: 2,
        type: 'string',
        nullable: false,
        dependsOn: [],
      },
      {
        key: 'privateDerived',
        label: 'PRIVATE_DERIVED_LABEL_SENTINEL',
        index: 3,
        type: 'string',
        nullable: false,
        dependsOn: ['private'],
      },
    ],
  }
}
