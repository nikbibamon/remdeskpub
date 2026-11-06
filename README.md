# Tvijo RemDesk for Claude Code

This repository is the MIT-licensed, root-folder Claude Code plugin source for
Tvijo RemDesk. It adds one skill, `inspect-project`, and configures the remote
MCP endpoint `https://mcp.tvijo.com/mcp` over HTTP.

**Publisher:** Tvijo, independently operated by individual maintainer Nik
Bibamon. **Support:** [admin@tvijo.com](mailto:admin@tvijo.com).

## What it does

The `inspect-project` skill helps Claude list and read a small set of files from
the project the user has authorized, then explain the findings with file
references. The skill itself does not write files or run commands.

The remote server controls the tools and access available to an account. It may
offer file writes, approved command execution, or bounded task delegation when
the relevant account and host policies permit them. The plugin does not make
the connection read-only, grant access to a host, or bypass an authorization
decision. Review the current MCP tool list and server permissions before use,
and use a separate test workspace for any write or execution operation.

RemDesk is separate from RootRemDesk and TvijoTerm. This plugin does not enable
root access or payments.

## Install and connect

The public setup guide is planned for GitHub Pages. Its source and intended
English/Russian URLs are:

- [English OAuth guide source](docs/index.html) · planned hosted page:
  <https://nikbibamon.github.io/remdeskpub/>
- [Инструкция по OAuth на русском](docs/ru.html) · планируемая страница:
  <https://nikbibamon.github.io/remdeskpub/ru.html>

The hosted pages are not claimed live until GitHub Pages publication is
verified. To load the plugin from a local clone, use Claude Code's
`--plugin-dir` option:

```sh
git clone https://github.com/nikbibamon/remdeskpub.git
claude plugin validate --strict ./remdeskpub

# From the project directory you are authorized to inspect:
claude --plugin-dir /absolute/path/to/remdeskpub
```

In the Claude Code session, inspect `/mcp` and the tools available from
`plugin:tvijo-remdesk:remdesk`. If access is already approved for your account,
follow the service's OAuth consent flow in the browser and review the requested
access before approving it. Then ask Claude to inspect the specific authorized
directory, or run:

```text
/tvijo-remdesk:inspect-project
```

Authorization is a service-side prerequisite. Installing this plugin does not
create a RemDesk identity, approve an account, or provide a reviewer login. The
owner's OAuth approval token is private operator material: never request it,
paste it into Claude, or put it in a repository. The end-to-end Claude OAuth
and reviewer flows have not been tested for this public source release; if your
account is not already approved, contact support to ask about access.

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

This is version 0.1.0, the first public source release. It is **not** a Claude
Directory or marketplace submission. OAuth, reviewer access and end-to-end tool
tests are not verified by this repository; prepared checks remain marked not
run in [`docs/review-cases.json`](docs/review-cases.json) and
[`docs/reviewer-guide.md`](docs/reviewer-guide.md).

## Registration and reviewer materials

- [English connector copy sheet](docs/listing.en.json)
- [Русский лист описания коннектора](docs/listing.ru.json)
- [Reviewer guide](docs/reviewer-guide.md)
- [Prepared review cases](docs/review-cases.json)

The JSON files are copy sheets, not a Claude portal import format. Directory
categories, listing status, and authentication readiness must be verified in
the actual authenticated portal before submission.
