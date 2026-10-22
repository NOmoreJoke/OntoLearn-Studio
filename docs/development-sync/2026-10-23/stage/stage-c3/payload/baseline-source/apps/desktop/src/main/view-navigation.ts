import type { WebContents } from 'electron'

// Same-document anchors/history keep the renderer mounted and its subscriptions
// alive. Only a new main document needs a new task-view generation.
export function installViewNavigation(
  contents: Pick<WebContents, 'on'>,
  replaceDocument: () => void,
): void {
  contents.on('did-start-navigation', (details) => {
    if (details.isMainFrame && !details.isSameDocument) replaceDocument()
  })
}
