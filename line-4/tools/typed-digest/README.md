# Offline EIP-712 digest checker

This Python standard-library tool calculates the domain separator, message struct hash, and final EIP-712 digest from a typed-data JSON request. It checks field names, Solidity value ranges, array lengths, hex lengths, and duplicate JSON keys. It makes no network call and never signs. Round 22 hardens the input boundary identified in the gathering review without changing the goal or existing valid example hashes.

From the repository root, run:

```sh
python3 -B line-4/tools/typed-digest/typed_digest.py line-4/tools/typed-digest/zto-example.json --expect 0xc292388738e2cf2c7f57b9b8926821aff508ed38c1b355020cc7dc459dbbb8cb
```

The command exits 0 and prints `matchesExpected: true` alongside the domain separator, message hash, and digest. The example refers to ZTO's actual Ethereum token address and is illustrative typed data, not a token permit or a claim that ZTO accepts this message. Replace the input path and expected digest with the exact typed-data JSON and digest shown by the client for a meaningful comparison. Include its `EIP712Domain` type. A digest mismatch exits 1; malformed or out-of-bounds input exits 2 with an error on stderr and no success JSON. Omit `--expect` to calculate without comparing.

Run the complete offline check from the repository root:

```sh
python3 -B -m unittest discover -s line-4/tools/typed-digest -p 'test_*.py' -v
```

Tried on 2026-10-14: all 28 tests passed, including the four ancestor tests. The ZTO example retained its original digest and the published [EIP-712 Ether Mail example](https://eips.ethereum.org/EIPS/eip-712) retained its domain separator, message hash, and final digest. Added checks cover signed integer extension and limits, byte padding, empty and nested arrays, recursive types with finite values, schema ordering, and cached-schema stability. Hostile-input tests cover duplicate keys, floats and nonfinite values, invalid UTF-8 and lone surrogates, oversized files, deep nesting, cyclic Python values, path traversal, symlinked files/directories, FIFO rejection without blocking, and CLI exit codes. No network, dependencies, wallet, or transaction is needed.

The CLI reads only regular files beneath the **current working directory**. Run it from the workspace that contains the input. Absolute paths under that directory also work. Parent traversal, hidden path components, and all symlinks are rejected. POSIX directory descriptors and no-follow opens prevent symlink substitution during traversal; the CLI refuses to run on platforms lacking those primitives. It reads at most 65,537 bytes and rejects inputs over 65,536 bytes, including a file that grows after its initial size check. It does not inspect environment variables or configuration. Tests create temporary nonsecret fixtures in this tool folder and remove them on completion.

Fixed resource limits are deliberately narrower than the entire EIP-712 input space:

| Limit | Maximum |
| --- | ---: |
| UTF-8 JSON file | 65,536 bytes |
| JSON nesting / in-memory tree depth | 48 |
| Visited values and object keys | 8,192 |
| Struct declarations | 64 |
| Fields across all declarations | 256 |
| Struct and field identifier length | 128 characters |
| Field type expression length | 256 characters |
| Array dimensions per type | 8 |

The JSON parser checks nesting before decoding. The public `digest(data)` Python function also validates depth, node count, total string bytes, Unicode, integer magnitude, and cycles before encoding. Floating-point JSON literals (even `1.0` and `1e3`) are refused; use integers or canonical decimal/hex integer strings. Recursive type definitions remain supported when the actual message is finite. Type encodings and type hashes are cached per encoder against a copied schema. The lower-level `Encoder` helpers are for already validated values; do not mutate `encoder.types` or use those helpers as the untrusted-input boundary.

These are finite work limits, not a hard wall-clock sandbox. The working directory is caller-selected, not an operating-system isolation boundary. The tool does not establish whether a signing request is safe, protect against replay, or prove a contract will honor it; it checks the bytes implied by the supplied typed data.
