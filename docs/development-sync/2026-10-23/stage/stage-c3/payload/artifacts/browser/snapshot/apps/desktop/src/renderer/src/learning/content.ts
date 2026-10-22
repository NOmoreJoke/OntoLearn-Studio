import course from '../../../../../../content/learning/course.json'
import glossary from '../../../../../../content/learning/glossary.json'
import type { Course, GlossaryEntry } from './types'

// Bundled read-only content; no filesystem, network, credential or model dependency.
export const offlineCourse: Course = course
export const offlineGlossary: readonly GlossaryEntry[] = glossary.entries
