# agent-runbooks

A repository of **agent runbooks** — structured markdown documents that tell a coding agent how to accomplish complex, multi-step tasks with evaluation loops and quality gates.

Each runbook can be deployed via **Docker** or run on **[jetty.io](https://jetty.io)**.

## Layout

Runbooks are organized by collection:

```
runbooks/
  {collection}/
    {runbook_name}/
      RUNBOOK.md
```

Every runbook lives in its own directory and is authored as a single `RUNBOOK.md` file alongside any supporting assets (datasets, prompts, fixtures).

## Running a runbook

### Via Docker

Each runbook can be executed in a container that mounts the runbook directory and runs an agent against it. See the runbook's own README or the `tools/` directory for collection-specific Compose configurations.

### Via jetty.io

Runbooks are first-class assets on [jetty.io](https://jetty.io). Upload a runbook to a collection and Jetty will orchestrate execution, capture trajectories, and surface evaluation results in the dashboard.

See the [Jetty documentation](https://jetty.io/docs) for details on deploying and monitoring runbooks.

## License

[MIT](./LICENSE)
