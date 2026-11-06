# Tvijo RemDesk for Claude Code

This repository is the MIT-licensed, root-folder Claude Code plugin source for
Tvijo RemDesk. It adds one skill, `inspect-project`, and configures the remote
MCP endpoint `https://mcp.tvijo.com/mcp` over HTTP.

**Publisher:** Tvijo, independently operated by individual maintainer Nik
Bibamon. **Support:** [admin@tvijo.com](mailto:admin@tvijo.com).

## Scope and readiness

The bundled skill guides bounded listing and reading of an explicitly authorized
project. The private RemDesk server code now implements the customer-scoped,
read-only pilot for `remdesk_fs_list` and `remdesk_fs_read`. Local synthetic
integration passed with two accounts and eight HTTP checks, including refresh,
rotation, revocation and isolation. The Gateway pilot and ledger suite passed
14 tests; the Go run recorded 106 test events across 10 packages, and `go vet`
passed. These results are local evidence, not production or Claude-client
verification.

A one-selected-account production pilot was verified on 2026-11-06 at
15:43:10 UTC. The live MCP resource advertises only `mcp:read`; its public
unauthorized challenge, DCR and Claude callback/loopback checks passed. The
customer pilot is restricted to that selected account and synthetic fixtures.
This does not mean that all 11 operator tools are customer-accessible: their
all 11 operator tools have titles and the four applicable safety annotations
pass; this does not make those tools customer-accessible. Customer dispatch is
read-only. A real Claude client flow remains `NOT_RUN`, so this package is
**not ready for Claude Directory submission**. Do not use or share the host
operator approval token. Before submission, test the exact deployed catalog and
every advertised tool with the reviewer account.

Write, command-execution and delegation capabilities belong to the separate
operator service and are not part of this proposed customer listing. The skill
does not constrain server-side permissions. This plugin is separate from
RootRemDesk and TvijoTerm; it does not enable root access or payments.

## Install and connect

The HTML guide is public on GitHub Pages. The corrections in this source
checkout have not yet been published to those pages:

- [English step-by-step guide](https://nikbibamon.github.io/remdeskpub/)
- [Пошаговая инструкция на русском](https://nikbibamon.github.io/remdeskpub/ru.html)

It covers the connector and optional plugin registration paths, the limited
pilot and remaining Claude/reviewer checks. Use the
[connector copy sheet](https://github.com/nikbibamon/remdeskpub/blob/main/docs/connector-listing.en.json)
for the MCP connector and the
[plugin copy sheet](https://github.com/nikbibamon/remdeskpub/blob/main/docs/listing.en.json)
for this optional bundle. Public protocol checks and isolated source tests are
recorded in [the diagnostic result](https://github.com/nikbibamon/remdeskpub/blob/main/docs/oauth-status.json).
The production pilot receipt is separate from local tests; neither proves a
real Claude client session or tool call.

To validate and load the plugin from a local clone, use Claude Code's
`--plugin-dir` option:

```sh
git clone https://github.com/nikbibamon/remdeskpub.git
claude plugin validate --strict ./remdeskpub

# From the project directory you are authorized to inspect:
claude --plugin-dir /absolute/path/to/remdeskpub
```

In Claude Code, inspect `/mcp` and the tools available from
`plugin:tvijo-remdesk:remdesk`. Do not infer that the proposed customer pilot
has been deployed from the plugin configuration or public OAuth discovery. Do
not enter, request, copy or share the host operator approval token. Installing
the plugin does not create a RemDesk identity, approve an account, or provide a
reviewer login.

## Privacy and review status

The published [privacy notice](https://dsh.tvijo.com/privacy) says RemDesk
authorization, audit, usage and job records may persist without a fixed
automatic deletion period. Erasure requests can remain pending safe writer
coordination; the described flow does not delete individual messages or
automatically erase a whole account. Revocation does not erase audit/usage
records or data already returned to an AI client. Provider and backup copies
require separate handling. This plugin does not add or promise deletion
controls or a retention deadline. See the
[product rules](https://dsh.tvijo.com/product-rules).

Plugin version 0.1.1 is not a Claude Directory or marketplace submission. The
copy sheets distinguish local integration results from the verified limited
pilot. Real Claude authorization and tool calls remain `NOT_RUN`; Directory
readiness remains pending. See
[`docs/review-cases.json`](docs/review-cases.json) and
[`docs/reviewer-guide.md`](docs/reviewer-guide.md).

## Registration and reviewer materials

- [English connector copy sheet](docs/connector-listing.en.json)
- [Русский лист описания коннектора](docs/connector-listing.ru.json)
- [English plugin copy sheet](docs/listing.en.json)
- [Русский лист описания плагина](docs/listing.ru.json)
- [Reviewer guide](docs/reviewer-guide.md)
- [Prepared review cases](docs/review-cases.json)

The JSON files are copy sheets, not a Claude portal import format. Directory
categories, listing status, account readiness and authentication must be
verified in the authenticated portal and on the deployed endpoint before
submission.
