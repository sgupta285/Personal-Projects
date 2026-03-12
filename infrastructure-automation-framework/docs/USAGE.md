# Usage Guide

## Service config shape

Service configs are TOML files with sections such as:
- `[service]`
- `[container]`
- `[runtime]`
- `[deploy]`
- `[[env_vars]]`

## Environment config shape

Environment configs include:
- `[environment]`
- `[terraform]`
- `[[secrets]]`

## Rollout config shape

Rollout configs include:
- `[service]`
- `[environment]`
- `[strategy]`
- `[[checks]]`
- `[[abort_conditions]]`
