# JC AI Operating System — Admin MVP

This branch adds a first local-first admin interface at `web/index.html`.

## Run it locally

1. Download or clone this branch.
2. Open `web/index.html` directly in a modern browser, or serve the `web` directory with any static HTTP server.
3. Create tasks, add leads, record income/expenses and save knowledge notes.

No API key or backend is required for this initial interface slice. Entries are stored in the current browser's localStorage, so they are not cloud-synced and can be lost if browser data is cleared. Export/backup is not implemented yet.

## Current scope

- Command center with task, lead and manually recorded revenue metrics
- Task creation, priority, status and deletion
- Specialist role registry for coordinator, engineering, research, finance, sales, real estate, operations and support
- Customer/lead list
- Manual income/expense log
- Knowledge notes

## Important limitations

This is a **first MVP slice**, not a fully autonomous operating system or complete software agency. It currently has no authentication, multi-user access control, cloud database, AI provider integration, live execution engine, real accounting/bank connection, messaging integration or deployed production hosting. Agent departments are role definitions, not running independent agents. Do not enter secrets or sensitive customer/financial data.

## Next implementation slices

1. Add tests and connect the dashboard to the existing FastAPI backend.
2. Implement authentication and server-side authorization before remote access.
3. Add persistent database-backed customers, projects, finance records and audit events.
4. Add an AI provider abstraction with a local/offline option and optional API-key configuration.
5. Add a governed task runner, tool permissions, approval queue and emergency stop.
6. Add integrations one at a time with tests, explicit permissions and failure handling.
7. Add deployment, backups, monitoring and production readiness checks.

Each slice must be tested and reviewed before adding the next. Free tiers and open-source software can reduce costs, but hosting, APIs and external integrations may have fees.
