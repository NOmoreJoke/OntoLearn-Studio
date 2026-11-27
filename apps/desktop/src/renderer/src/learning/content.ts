import glossary from '../../../../../../content/learning/glossary.json'
import course from './offline-course.json'
import fixtureInputs from './task-fixture-inputs.json'
import type { Course, GlossaryEntry } from './types'

// Renderer projection of the offline course. Authenticated demonstrations are
// delivered by the engine after recording assistance.
export const offlineCourse: Course = course
export const offlineGlossary: readonly GlossaryEntry[] = glossary.entries

export type LearningFixtureTaskId = 'quality' | 'transfer-repair' | 'transfer-classify'

export function supportsLearningFixture(taskId: string): taskId is LearningFixtureTaskId {
  return taskId === 'quality' || taskId === 'transfer-repair' || taskId === 'transfer-classify'
}

const initialData = {
  quality: fixtureInputs.lx01,
  'transfer-repair': { ontology: fixtureInputs.transferOntology, ...fixtureInputs.repair },
  'transfer-classify': {
    ontology: fixtureInputs.transferOntology,
    ...fixtureInputs.classification,
  },
}

// Initial input only, projected from the versioned course prerequisites and
// transfer datasets. Consumers receive a disposable copy of the read-only seed.
export function learningFixtureData<T extends LearningFixtureTaskId>(
  taskId: T,
): (typeof initialData)[T] {
  return structuredClone(initialData[taskId])
}
