#!/usr/bin/env python3
"""Bounded, unauthenticated OAuth/MCP diagnostic for Tvijo RemDesk.

This script contacts one fixed HTTPS origin. It never registers a client,
requests consent, obtains or submits a token, or calls a RemDesk tool.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPSHandler, HTTPRedirectHandler, Request, build_opener

ORIGIN = "https://mcp.tvijo.com"
RESOURCE = ORIGIN + "/mcp"
TIMEOUT_SECONDS = 8
MAX_RESPONSE_BYTES = 64 * 1024
OUTPUT = Path(__file__).resolve().parents[1] / "docs" / "oauth-status.json"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


OPENER = build_opener(HTTPSHandler(), NoRedirect())


def request(method: str, path: str, body: bytes | None = None,
            content_type: str | None = None, authorization: str | None = None):
    headers = {"Accept": "application/json"}
    if content_type:
        headers["Content-Type"] = content_type
    if authorization:
        headers["Authorization"] = authorization
    req = Request(ORIGIN + path, data=body, headers=headers, method=method)
    try:
        response = OPENER.open(req, timeout=TIMEOUT_SECONDS)
    except HTTPError as err:
        response = err
    except (URLError, TimeoutError, OSError) as err:
        return {"status": None, "headers": {}, "json": None,
                "transport_error": type(err).__name__}
    try:
        raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            return {"status": response.status, "headers": {}, "json": None,
                    "transport_error": "response_too_large"}
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            data = None
        return {"status": response.status,
                "headers": {k.lower(): v for k, v in response.headers.items()},
                "json": data, "transport_error": None}
    finally:
        response.close()


def check(name: str, ok: bool, status: int | None, detail: str):
    return {"name": name, "result": "PASS" if ok else "FAIL",
            "http_status": status, "detail": detail}


def string_list(value):
    """Treat only JSON arrays of strings as string lists; never iterate scalars."""
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def safe_scopes(value):
    """Keep only short OAuth scope tokens; never copy URLs or arbitrary text."""
    return sorted({item for item in string_list(value)
                   if re.fullmatch(r"[A-Za-z0-9:_-]{1,64}", item)})


def bearer_challenge_matches(header: str, expected_metadata: str) -> bool:
    """Require a Bearer challenge carrying the exact protected-resource URL."""
    bearer = re.search(
        r"(?:^|,)\s*Bearer\s+(.+?)(?=,\s*[A-Za-z][A-Za-z0-9_-]*\s+|$)",
        header, flags=re.IGNORECASE)
    if not bearer:
        return False
    metadata = re.search(
        r'\bresource_metadata\s*=\s*(?:"([^"]+)"|([^,\s]+))',
        bearer.group(1), flags=re.IGNORECASE)
    return bool(metadata and (metadata.group(1) or metadata.group(2)) == expected_metadata)


def run():
    checks = []

    protected = request("GET", "/.well-known/oauth-protected-resource")
    protected_doc = protected["json"] if isinstance(protected["json"], dict) else {}
    checks.append(check(
        "protected_resource_discovery",
        protected["status"] == 200
        and protected_doc.get("resource") == RESOURCE
        and string_list(protected_doc.get("authorization_servers")) == [ORIGIN]
        and bool({"mcp", "mcp:read"} & set(string_list(protected_doc.get("scopes_supported")))),
        protected["status"], "HTTPS metadata matches the expected protected resource and issuer."))

    server = request("GET", "/.well-known/oauth-authorization-server")
    server_doc = server["json"] if isinstance(server["json"], dict) else {}
    checks.append(check(
        "authorization_server_discovery",
        server["status"] == 200
        and server_doc.get("issuer") == ORIGIN
        and server_doc.get("authorization_endpoint") == ORIGIN + "/oauth/authorize"
        and server_doc.get("token_endpoint") == ORIGIN + "/oauth/token"
        and server_doc.get("registration_endpoint") == ORIGIN + "/oauth/register"
        and "code" in string_list(server_doc.get("response_types_supported"))
        and "authorization_code" in string_list(server_doc.get("grant_types_supported"))
        and "none" in string_list(server_doc.get("token_endpoint_auth_methods_supported"))
        and "S256" in string_list(server_doc.get("code_challenge_methods_supported")),
        server["status"], "Issuer, endpoints, authorization-code flow, public-client auth, and PKCE S256 are checked."))

    rpc = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list",
                      "params": {}}, separators=(",", ":")).encode()
    anonymous = request("POST", "/mcp", rpc, "application/json")
    challenge = anonymous["headers"].get("www-authenticate", "")
    checks.append(check(
        "anonymous_tools_list_rejected",
        anonymous["status"] == 401 and bearer_challenge_matches(
            challenge, ORIGIN + "/.well-known/oauth-protected-resource"),
        anonymous["status"], "Unauthenticated read-only tools/list request must be challenged."))

    invalid = request("POST", "/mcp", rpc, "application/json",
                      "Bearer deliberately-invalid-diagnostic-value")
    checks.append(check(
        "synthetic_invalid_bearer_rejected",
        invalid["status"] == 401,
        invalid["status"], "Synthetic non-credential bearer must be rejected."))

    all_passed = all(item["result"] == "PASS" for item in checks)
    # No authenticated request is made. In particular, this diagnostic never
    # registers a client or obtains/uses consent, authorization codes or tokens.
    return {
        "schema": "tvijo-remdesk-oauth-diagnostic-v1",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "advertised_capabilities": {
            "advertised_scopes": safe_scopes(protected_doc.get("scopes_supported")),
            "scope_enforcement": "NOT_TESTED_BY_THIS_DIAGNOSTIC",
            "customer_scope_in_challenge": bool(re.search(
                r'\bscope\s*=\s*"mcp:read"(?:\s*,|\s*$)', challenge)),
            "pkce_s256": "S256" in string_list(server_doc.get("code_challenge_methods_supported")),
            "authorization_code_response": "code" in string_list(server_doc.get("response_types_supported")),
            "client_authentication_none": "none" in string_list(server_doc.get("token_endpoint_auth_methods_supported")),
            "authorization_code_grant": "authorization_code" in string_list(server_doc.get("grant_types_supported")),
            "refresh_token_grant": "refresh_token" in string_list(server_doc.get("grant_types_supported")),
            "dynamic_client_registration": server["status"] == 200 and isinstance(
                server_doc.get("registration_endpoint"), str),
        },
        "registration_or_consent": "NOT_RUN",
        "authenticated_tools_list": "NOT_RUN",
        "claude_end_to_end_oauth": "NOT_RUN",
        "fully_integrated": False,
        "summary": (("Unauthenticated protocol checks passed." if all_passed else
                     "One or more unauthenticated protocol checks failed or could not be observed.")
                    + " This does not prove client registration, per-user sign-in and consent, "
                    "authenticated tools/list, or Claude end-to-end compatibility."),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-status", action="store_true",
                        help="write sanitized results to docs/oauth-status.json")
    args = parser.parse_args()
    result = run()
    if args.write_status:
        # Preserve the separately verified isolated-test receipt when refreshing
        # public HTTP checks; this script itself never runs source tests.
        try:
            previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = {}
        for key in ("isolated_source_test", "runtime_verification", "submission_readiness"):
            observed = previous.get(key)
            if isinstance(observed, dict):
                result[key] = observed
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        OUTPUT.write_text(rendered, encoding="utf-8")
    else:
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    print(rendered, end="")
    return 0 if all(item["result"] == "PASS" for item in result["checks"]) else 1


if __name__ == "__main__":
    sys.exit(main())
