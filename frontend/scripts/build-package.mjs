import { mkdir, mkdtemp, rm } from 'node:fs/promises'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import os from 'node:os'
import path from 'node:path'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const output = path.join(root, 'dist', 'search-0.1.0.tgz')
await rm(path.join(root, 'dist'), { recursive: true, force: true })
await mkdir(path.dirname(output), { recursive: true })
const staging = await mkdtemp(path.join(os.tmpdir(), 'search-frontend-'))

try {
  const deploy = spawnSync('corepack', [
    'pnpm', '--filter', '@open-city-planner/search',
    'deploy', '--prod', '--legacy', '--frozen-lockfile', staging
  ], { cwd: root, stdio: 'inherit' })
  if (deploy.status !== 0) process.exit(deploy.status ?? 1)

  const archive = spawnSync('tar', [
    '--sort=name', '--mtime=UTC 1980-01-01', '--owner=0', '--group=0', '--numeric-owner',
    '-czf', output, 'package.json', 'module.json', 'layer'
  ], { cwd: staging, stdio: 'inherit' })
  if (archive.status !== 0) process.exit(archive.status ?? 1)
  console.log(output)
} finally {
  await rm(staging, { recursive: true, force: true })
}
