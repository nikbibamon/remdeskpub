# Changelog

## 0.1.1 — 2026-11-06

Refresh the owner and reviewer materials with current implementation and test
evidence while keeping production and Claude-client status explicit.

- Document private RemDesk code for customer-scoped `remdesk_fs_list` and
  `remdesk_fs_read`; keep the public plugin source separate from the server.
- Record the local synthetic two-account integration (eight HTTP checks,
  including refresh, rotation, revocation and isolation), 14 Gateway pilot and
  ledger tests, 106 Go test events across 10 packages, and passing `go vet`.
- Record the one-selected-account production pilot as live-verified on
  2026-11-06 at 15:43:10 UTC, limited to `mcp:read` and synthetic fixtures.
  Keep real Claude client authorization and tool calls `NOT_RUN`.
- Keep the listing unsubmitted and retain the reviewer account, exact deployed
  catalog and per-tool checks as pre-submission gates.

These results do not establish a real Claude client connection, Directory
readiness, approval or publication, and do not change the license.

## 0.1.0 — 2026-11-06

First public MIT-licensed source release of the root-folder Claude Code plugin.

- Add the `inspect-project` skill for bounded listing and reading of a user-
  authorized project.
- Configure Claude Code to connect to `https://mcp.tvijo.com/mcp` using remote
  HTTP MCP.
- Add English and Russian copy sheets, a reviewer guide and prepared test cases.
- Include a synthetic sample project for bounded reviewer checks.

This release does not mean the Claude Directory submission, OAuth flow,
reviewer access, or full tool runtime has been approved or tested. See the
readiness statements in the README and reviewer materials.
