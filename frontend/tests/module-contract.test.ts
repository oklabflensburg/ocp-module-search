import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

const root = fileURLToPath(new URL('..', import.meta.url))
const definition = JSON.parse(readFileSync(`${root}/module.json`, 'utf8'))

describe('Search frontend module contract', () => {
  it('declares the current neutral full-stack module shape', () => {
    expect(definition).toEqual({
      schemaVersion: 1,
      id: 'search',
      version: '0.1.0',
      backendModuleId: 'search',
      compatibility: {
        host: '>=1.0.0 <2.0.0',
        sdk: '>=1.5.0 <2.0.0',
        backend: '>=0.1.0 <0.2.0'
      },
      layer: 'layer',
      requires: { modules: {} },
      publicContributions: {
        routes: [],
        ui: [],
        map: { sources: [], layers: [] },
        sitemap: { staticRoutes: [], dynamicRoutes: [] }
      }
    })
  })

  it('does not claim Search UI or route contributions during bootstrap', () => {
    expect(definition.publicContributions.routes).toEqual([])
    expect(definition.publicContributions.ui).toEqual([])
    expect(definition.publicContributions.map).toEqual({ sources: [], layers: [] })
  })
})
