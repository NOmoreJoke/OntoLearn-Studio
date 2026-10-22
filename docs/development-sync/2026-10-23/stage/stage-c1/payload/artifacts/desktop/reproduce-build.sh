#!/bin/zsh
set -euo pipefail
stage_tree='/Users/kyle/Documents/工作/知爻/本体/.worktrees/stage-acceptance-20261022'
stage_output='/Users/kyle/Documents/工作/知爻/本体/outputs/20261022_stage_acceptance/desktop'
cd "$stage_tree"
[[ "$(git rev-parse HEAD)" == '5f910b52c69d86a1076b2032e5d3c63e715947f3' ]]
export UV_CACHE_DIR="$stage_output/.cache/uv"
export ELECTRON_CACHE="$stage_output/.cache/electron"
export ELECTRON_BUILDER_CACHE="$stage_output/.cache/electron-builder"
export npm_config_cache="$stage_output/.cache/npm"
npm ci
uv sync --frozen
npm run typecheck
npm run package:dir
cd apps/desktop
../../node_modules/.bin/electron-builder --dir --publish never \
  --config.productName='OntoLearn Stage Acceptance 20261022' \
  --config.appId='io.github.nomorejoke.ontolearnstudio.stageacceptance20261022' \
  --config.extraMetadata.name='ontolearn-stage-acceptance-20261022' \
  --config.extraMetadata.productName='OntoLearn Stage Acceptance 20261022' \
  --config.directories.output="$stage_output/build-stage"
# Does not launch the app. Move the generated .app into a NEW output directory,
# run probe-packaged-engine.py there, and regenerate all hashes before delivery.
