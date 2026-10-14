#!/usr/bin/env python3
"""Capture bounded, read-only Ethereum JSON-RPC evidence as portable JSON."""

from datetime import datetime, timezone
import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request


DEFAULT_RPC = "https://ethereum-rpc.publicnode.com"
ZTO = "0xd782bdea4ef02a0bd391eb9089470c8080f0a68e"
MAX_RESPONSE = 2_000_000
MAX_REQUEST = 16_384
HEX = re.compile(r"^0x[0-9a-fA-F]*$")
ADDRESS = re.compile(r"^0x[0-9a-fA-F]{40}$")
HASH = re.compile(r"^0x[0-9a-fA-F]{64}$")
READ_METHODS = frozenset({
    "eth_chainId", "eth_blockNumber", "eth_getBalance", "eth_getCode",
    "eth_getTransactionReceipt", "eth_getBlockByNumber", "eth_call",
})


class SnapshotError(Exception):
    """A rejected request, transport failure, or invalid RPC answer."""


def require(condition, message):
    if not condition:
        raise SnapshotError(message)


def block_tag(value):
    return (value in ("earliest", "latest", "safe", "finalized") or
            (isinstance(value, str) and bool(re.fullmatch(r"0x[0-9a-fA-F]+", value))))


def validate_request(method, params):
    """Only permit public state reads with bounded, typed parameters."""
    require(isinstance(method, str) and method in READ_METHODS,
            f"method is not an allowed public read: {method}")
    require(isinstance(params, list), "params must be a JSON array")
    if method in ("eth_chainId", "eth_blockNumber"):
        require(params == [], f"{method} takes no parameters")
    elif method in ("eth_getBalance", "eth_getCode"):
        require(len(params) == 2 and isinstance(params[0], str) and
                bool(ADDRESS.fullmatch(params[0])) and block_tag(params[1]),
                f"{method} requires [address, block tag]")
    elif method == "eth_getTransactionReceipt":
        require(len(params) == 1 and isinstance(params[0], str) and
                bool(HASH.fullmatch(params[0])), "receipt requires one transaction hash")
    elif method == "eth_getBlockByNumber":
        require(len(params) == 2 and block_tag(params[0]) and
                type(params[1]) is bool, "block read requires [block tag, boolean]")
    elif method == "eth_call":
        require(len(params) == 2 and isinstance(params[0], dict) and
                set(params[0]) == {"to", "data"} and block_tag(params[1]),
                "eth_call requires [{to, data}, block tag]")
        call = params[0]
        require(isinstance(call["to"], str) and bool(ADDRESS.fullmatch(call["to"])),
                "eth_call.to must be an address")
        data = call["data"]
        require(isinstance(data, str) and len(data) <= 4098 and
                len(data) % 2 == 0 and bool(HEX.fullmatch(data)),
                "eth_call.data must be bounded even-length hex")


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise SnapshotError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise SnapshotError(f"non-JSON number: {value}")


def parse_json(raw):
    try:
        return json.loads(raw, object_pairs_hook=unique_pairs,
                          parse_constant=reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"invalid JSON response: {exc}") from exc


def validate_response(value):
    require(isinstance(value, dict), "RPC response must be an object")
    require(value.get("jsonrpc") == "2.0" and type(value.get("id")) is int and
            value["id"] == 1, "RPC version or request ID mismatch")
    require(("result" in value) != ("error" in value),
            "RPC response needs exactly one of result or error")
    if "error" in value:
        error = value["error"]
        require(isinstance(error, dict) and type(error.get("code")) is int and
                isinstance(error.get("message"), str), "malformed RPC error")
        raise SnapshotError(f"RPC error {error['code']}: {error['message']}")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise SnapshotError("RPC endpoint redirected; refusing another destination")


def rpc_call(url, method, params, timeout):
    parts = urllib.parse.urlsplit(url)
    require(parts.scheme == "https" and bool(parts.hostname) and
            parts.username is None and parts.password is None and
            not parts.fragment, "RPC URL must be HTTPS without credentials or fragment")
    validate_request(method, params)
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                       "params": params}, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")
    require(len(body) <= MAX_REQUEST, "RPC request exceeds byte limit")
    request = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Encoding": "identity",
        "User-Agent": "IdentityMD-Line1-BoundedSnapshot/2.0",
    })
    # An empty ProxyHandler prevents urllib from consulting proxy environment variables.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            require(response.status == 200, f"HTTP {response.status}")
            raw = response.read(MAX_RESPONSE + 1)
            require(len(raw) <= MAX_RESPONSE, "RPC response exceeds byte limit")
            content_type = response.headers.get("Content-Type", "")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SnapshotError(f"RPC transport failed: {exc}") from exc
    answer = parse_json(raw)
    validate_response(answer)
    return content_type, answer


def make_snapshot(url, method, params, timeout):
    content_type, response = rpc_call(url, method, params, timeout)
    canonical = json.dumps(response, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8")
    return {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "rpc_url": url,
        "content_type": content_type,
        "request": {"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        "response": response,
        "response_sha256": hashlib.sha256(canonical).hexdigest(),
    }

