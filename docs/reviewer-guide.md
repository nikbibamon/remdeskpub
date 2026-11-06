# Reviewer guide

This guide describes a prepared review, not a completed test. The source package
is version 0.1.0 and has not been submitted to the Claude Directory or a
marketplace. All cases in [`review-cases.json`](review-cases.json) are marked
`NOT_RUN` unless a dated result is added after a real test.

## Before connecting

1. Review the public [privacy notice](https://dsh.tvijo.com/privacy) and
   [product rules](https://dsh.tvijo.com/product-rules). Records for
   authorization, audit, usage, and jobs may persist without a fixed automatic
   deletion deadline. An erasure request may wait for safe coordination, and
   revocation does not remove data already returned to an AI client.
2. Read the plugin source and the `.mcp.json` endpoint. It configures
   `https://mcp.tvijo.com/mcp` as a remote HTTP MCP server.
3. Confirm which tools and permissions the server actually offers to the
   reviewer identity. The bundled skill guides listing and reading only, but it
   does not constrain the server's other tools. Do not call write, execution,
   or delegation tools during the bounded fixture check.
4. Account access is service-owner approved. There is no self-service approval
   demonstrated by this package. The operator approval token is private; never
   request it, share it with a reviewer, or place it in this repository. The
   end-to-end Claude OAuth and reviewer setup have not been verified.

## Bounded fixture check

If a separate reviewer identity has been explicitly authorized for a disposable
test root, put `review-fixture/` inside that root. Clone this repository, then
run Claude Code from the authorized test project while loading the plugin:

```sh
git clone https://github.com/nikbibamon/remdeskpub.git
claude plugin validate --strict ./remdeskpub
cd /path/to/the/authorized/test/project
claude --plugin-dir /absolute/path/to/remdeskpub
```

After reviewing the project MCP entry and authenticating for that test account,
ask Claude to inspect only the fixture. The expected result identifies
`app.py:greeting`, cites `notes/release.txt`, and does not claim deployment.
Record actual tool names and results. Do not label setup, OAuth consent, or
validator output as a runtime fixture test.

## Test boundaries and readiness

The available sample supports a narrow listing/read test. It is not a test of
tenant isolation, symlink handling, command authorization, write protections,
task costs, or production data handling. Those checks require an isolated
reviewer workspace, a separate owner-approved account, and explicit scope. Any
delegated task also needs a numeric cost limit and an active test worker.

The connection may expose write, approved command, and delegation tools based
on server policy. The plugin skill does not revoke or limit those tools.
Confirm the live catalog each time and keep the review to the approved fixture.
Do not test root access, transfers, production paths, or unrestricted commands.

No completed Claude OAuth flow, reviewer credential, live end-to-end tool call,
Directory approval or marketplace publication is included or claimed. The public
HTML guides are verified at <https://nikbibamon.github.io/remdeskpub/> (English)
and <https://nikbibamon.github.io/remdeskpub/ru.html> (Russian). The separate
[diagnostic result](oauth-status.json) records public protocol and isolated
source tests; those do not prove reviewer access. Use connector-listing.en.json
for the server card and listing.en.json for the optional plugin card.
