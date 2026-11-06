# Reviewer guide

This guide describes prepared checks, not completed tests. The public source is
version 0.1.1 and has not been submitted to the Claude Directory or a
marketplace. Every case in [`review-cases.json`](review-cases.json) is
`NOT_RUN` unless a dated result is added after a real test.

## Current readiness and proposed scope

The private RemDesk implementation now supports a customer-scoped,
read-only pilot exposing `remdesk_fs_list` and `remdesk_fs_read`. Local
synthetic integration passed for two accounts in eight HTTP checks, including
refresh, rotation, revocation and isolation. The Gateway pilot and ledger suite
passed 14 tests; a Go run recorded 106 test events across 10 packages and
`go vet` passed. These are local test results, not evidence that production is
serving the tested revision.

The one-selected-account production pilot was verified on 2026-11-06 at
15:43:10 UTC. The production MCP resource advertises only `mcp:read`; its public
unauthorized challenge, DCR and Claude callback/loopback checks passed. The
pilot is limited to the selected account and synthetic fixtures. All 11 operator-catalog tools have titles and the four applicable safety
annotations pass. This does not make those tools customer-accessible: customer dispatch remains read-only. Real
Claude authorization and tool calls remain `NOT_RUN`. The package has not been
submitted to Claude Directory. Keep write, command-execution and delegation
tools outside the customer listing. Never use or share the host operator token.

## Before any future test

1. Review the public [privacy notice](https://dsh.tvijo.com/privacy) and
   [product rules](https://dsh.tvijo.com/product-rules). Authorization, audit,
   usage and job records may persist without a fixed automatic deletion
   deadline. Revocation does not remove data already returned to an AI client.
2. Read the plugin source and `.mcp.json`. The plugin configures
   `https://mcp.tvijo.com/mcp` as remote HTTP MCP; this does not prove that
   customer authorization or the proposed tools are live.
3. Use the already selected Platform account for the pilot. Do not create
   another account or use the host operator token. The live pilot is verified
   for `mcp:read`, but this has not been tested through a real Claude client.
4. Connect from Claude using that account, review the consent and approve only
   `mcp:read`. Then call MCP `tools/list`, record the customer-visible catalog
   and test each advertised tool with valid inputs on a disposable synthetic
   project. Stop if Claude requests broader access or exposes operator tools.

## Bounded fixture check

After the prerequisites above pass, place `review-fixture/` inside a disposable
authorized project root and use the same per-user reviewer identity that the
portal will receive. Clone this repository and validate the plugin:

```sh
git clone https://github.com/nikbibamon/remdeskpub.git
claude plugin validate --strict ./remdeskpub
cd /path/to/the/authorized/test/project
claude --plugin-dir /absolute/path/to/remdeskpub
```

In Claude Code, inspect `/mcp` and the tools available from
`plugin:tvijo-remdesk:remdesk`. For the planned two-tool pilot, make these
valid-input calls only if both tools are actually exposed to the reviewer:

- `remdesk_fs_list` with `{"path":"."}`
- `remdesk_fs_read` with `{"path":"README.md"}`

Record the returned results and time with sensitive project content removed.
Do not label setup, OAuth discovery, a consent screen, or validator output as a
runtime tool test. Do not claim that protocol discovery proves customer access.

## Test boundaries

The synthetic fixture supports a narrow listing/read check. Local integration
exercises two-account isolation, refresh/rotation and revocation; the
one-account production pilot has also passed its dated live verification. This
still does not prove that a real Claude client can complete authorization or
call tools. Do not test root access, transfers, production paths, or
unrestricted commands. Operator-only write, execution and delegation
capabilities are not part of the customer listing.

No real Claude OAuth flow, Claude tool call, Directory approval or marketplace
publication is included or claimed. The existing public guide URLs are
<https://nikbibamon.github.io/remdeskpub/> (English) and
<https://nikbibamon.github.io/remdeskpub/ru.html> (Russian); the corrections in
this source checkout have not yet been published to those pages. The separate
[diagnostic result](oauth-status.json) records protocol and local tests; it
does not prove production or real Claude access. Use
`connector-listing.en.json` for the connector copy and `listing.en.json` for
the optional plugin copy.
