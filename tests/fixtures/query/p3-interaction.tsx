import { createRoot } from 'react-dom/client'
import { QueryPage } from '../../../apps/desktop/src/renderer/src/query/QueryPage'

// Isolated component fixture only: no bridge, executor, persistence or model API.
const predicates = Array.from({ length: 17 }, (_, index) => ({
  iri: `urn:p${index + 1}`,
  label: `字段${String(index + 1).padStart(2, '0')}`,
}))
createRoot(document.getElementById('root')!).render(
  <QueryPage
    projectId="00000000-0000-4000-8000-000000000001"
    catalog={{ classes: [{ iri: 'urn:ClassA', label: '对象A' }], predicates }}
    alarmVocabulary={{ alarmClass: 'urn:ClassA', severity: 'urn:p1', status: 'urn:p2' }}
    savedQueries={[
      {
        definitionId: 'Saved-B',
        draft: {
          name: '已保存B',
          description: 'Synthetic saved definition, not persisted by this fixture',
          sparql: 'SELECT ?b WHERE { ?b a <urn:ClassB> }',
          scope: 'asserted',
          capabilityQuestion: 'B',
          source: 'editor',
        },
      },
    ]}
    modelDraft={{
      name: '模型M',
      description: 'Synthetic visible draft, no model call',
      sparql: 'SELECT ?m WHERE { ?m a <urn:ClassM> }',
      scope: 'asserted',
      capabilityQuestion: 'M',
      source: 'model',
    }}
  />,
)
