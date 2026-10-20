import { spawnSync } from 'node:child_process'
import { describe, expect, it } from 'vitest'
import { getEngineEnvironment } from '../../apps/desktop/src/main/engine'

const project = '00000000-0000-4000-8000-000000000001'
const fabricated: NodeJS.ProcessEnv = {
  HOME: '/fabricated/home',
  TMPDIR: '/fabricated/tmp',
  LANG: 'C.UTF-8',
  LC_CTYPE: 'UTF-8',
  TZ: 'UTC',
  PATH: '/fabricated/search-path',
  PYTHONPATH: '/fabricated/python-injection',
  PYTHONSTARTUP: '/fabricated/python-startup',
  PYTHONINSPECT: '1',
  LD_PRELOAD: '/fabricated/preload',
  LD_LIBRARY_PATH: '/fabricated/library-injection',
  DYLD_INSERT_LIBRARIES: '/fabricated/dyld-injection',
  OPENAI_API_KEY: 'artificial-not-a-credential',
  AWS_SESSION_TOKEN: 'artificial-not-a-credential',
  I04_API_SECRET_SENTINEL: 'artificial-not-a-credential',
  HTTP_PROXY: 'https://fabricated.invalid',
  HTTPS_PROXY: 'https://fabricated.invalid',
  NO_PROXY: '*',
  ONTOLEARN_DB_PATH: '/fabricated/unauthorized.db',
  ONTOLEARN_ALLOWED_PROJECTS: '["fabricated-unauthorized-project"]',
  ONTOLEARN_TEST_MODE: '1',
}

describe('explicit Python environment authority', () => {
  it('inherits only OS directories and locale and ignores all source authority/credentials', () => {
    expect(getEngineEnvironment(fabricated, {}, 'darwin')).toEqual({
      HOME: '/fabricated/home',
      TMPDIR: '/fabricated/tmp',
      LANG: 'C.UTF-8',
      LC_CTYPE: 'UTF-8',
      TZ: 'UTC',
      ONTOLEARN_ALLOWED_PROJECTS: '[]',
    })
    expect(getEngineEnvironment(fabricated, {}, 'linux')).toEqual(
      getEngineEnvironment(fabricated, {}, 'darwin'),
    )
  })
  it('issues DB, project authority and test mode only from explicit main options', () => {
    const env = getEngineEnvironment(
      fabricated,
      {
        dataPath: '/fabricated/authorized.db',
        allowedProjects: [project],
        testMode: true,
      },
      'linux',
    )
    expect(env.ONTOLEARN_DB_PATH).toBe('/fabricated/authorized.db')
    expect(env.ONTOLEARN_ALLOWED_PROJECTS).toBe(JSON.stringify([project]))
    expect(env.ONTOLEARN_TEST_MODE).toBe('1')
    expect(getEngineEnvironment(fabricated, { testMode: false }, 'linux')).not.toHaveProperty(
      'ONTOLEARN_TEST_MODE',
    )
    expect(fabricated.ONTOLEARN_DB_PATH).toBe('/fabricated/unauthorized.db')
  })
  it('normalizes Windows OS variable names without case-insensitive secret passthrough', () => {
    expect(
      getEngineEnvironment(
        {
          sYsTeMrOoT: 'C:\\Windows',
          windir: 'C:\\Windows',
          Temp: 'C:\\fabricated-temp',
          userprofile: 'C:\\fabricated-user',
          localappdata: 'C:\\fabricated-local',
          OPENAI_API_KEY: 'artificial-not-a-credential',
          openai_api_key: 'artificial-not-a-credential',
          Path: 'C:\\fabricated-search',
          ComSpec: 'C:\\fabricated-shell.exe',
        },
        {},
        'win32',
      ),
    ).toEqual({
      SystemRoot: 'C:\\Windows',
      WINDIR: 'C:\\Windows',
      TEMP: 'C:\\fabricated-temp',
      USERPROFILE: 'C:\\fabricated-user',
      LOCALAPPDATA: 'C:\\fabricated-local',
      ONTOLEARN_ALLOWED_PROJECTS: '[]',
    })
  })
  it('does not broaden an empty environment or mutate the caller dictionary', () => {
    const empty = Object.freeze({})
    expect(getEngineEnvironment(empty, {}, 'linux')).toEqual({ ONTOLEARN_ALLOWED_PROJECTS: '[]' })
    expect(empty).toEqual({})
  })
  it('actually launches a child without the fabricated credentials or injection variables', () => {
    const env = getEngineEnvironment(fabricated, { allowedProjects: [project] }, process.platform)
    const source = `process.stdout.write(JSON.stringify({
      secret: Object.hasOwn(process.env,'I04_API_SECRET_SENTINEL'),
      credential: Object.hasOwn(process.env,'OPENAI_API_KEY'),
      proxy: Object.hasOwn(process.env,'HTTP_PROXY'),
      injection: Object.hasOwn(process.env,'PYTHONPATH'),
      loader: Object.hasOwn(process.env,'LD_PRELOAD'),
      authority: JSON.parse(process.env.ONTOLEARN_ALLOWED_PROJECTS),
      testMode: Object.hasOwn(process.env,'ONTOLEARN_TEST_MODE')
    }))`
    const result = spawnSync(process.execPath, ['-e', source], {
      env,
      encoding: 'utf8',
      timeout: 5000,
    })
    expect(result.status).toBe(0)
    expect(result.stderr).toBe('')
    expect(JSON.parse(result.stdout)).toEqual({
      secret: false,
      credential: false,
      proxy: false,
      injection: false,
      loader: false,
      authority: [project],
      testMode: false,
    })
  })
})
