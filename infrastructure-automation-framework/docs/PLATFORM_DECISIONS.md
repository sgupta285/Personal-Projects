# Platform Decisions

## Why TOML for configs

TOML keeps the examples readable and avoids an extra YAML dependency. Python 3.11 includes `tomllib`, which makes the parser lightweight and stable.

## Why generated outputs are committed

For a portfolio repo, generated examples matter. They make the framework understandable immediately, even before the reviewer runs the CLI.

## Why there is a rollout planner

Deployment automation is not only about rendering files. Good platform tooling also captures operational intent, checks, and rollback thinking. The rollout planner makes that visible.
