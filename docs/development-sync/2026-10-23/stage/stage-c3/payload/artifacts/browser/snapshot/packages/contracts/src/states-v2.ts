import states from '../v2/states.json'
export function permitsTransition(
  from: string,
  to: string,
  beforeVersion: number,
  afterVersion: number,
  finalPersistedBeforeCancel: boolean,
): boolean {
  const next = states.transitions[from as keyof typeof states.transitions] as string[] | undefined
  return (
    !!next?.includes(to) &&
    Number.isSafeInteger(beforeVersion) &&
    beforeVersion >= 1 &&
    Number.isSafeInteger(afterVersion) &&
    afterVersion > beforeVersion &&
    !(from === 'cancelling' && to === 'succeeded' && !finalPersistedBeforeCancel)
  )
}
