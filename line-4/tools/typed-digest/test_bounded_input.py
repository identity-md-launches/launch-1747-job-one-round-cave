"""Boundary and encoding regressions; all fixtures stay beneath the working dir."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from typed_digest import (Encoder, MAX_ARRAY_DIMENSIONS, MAX_DEPTH, MAX_FIELDS,
                          MAX_INPUT_BYTES, MAX_NODES, MAX_TYPES, TypedDataError,
                          digest, keccak256, load_workspace_json, loads_bounded,
                          validate_tree)

HERE = Path(__file__).resolve().parent
EXAMPLE = HERE / "zto-example.json"
EXPECTED = "0xc292388738e2cf2c7f57b9b8926821aff508ed38c1b355020cc7dc459dbbb8cb"


class BoundedInputTests(unittest.TestCase):
    def setUp(self):
        # tempfile never uses a global or environment-derived temp directory.
        self.temp = tempfile.TemporaryDirectory(prefix="digest-test-", dir=HERE)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def put(self, name, raw):
        path = self.folder / name
        path.write_bytes(raw)
        return path

    def test_example_unchanged_and_absolute_path_supported(self):
        self.assertEqual(digest(load_workspace_json(EXAMPLE))["digest"], EXPECTED)

    def test_byte_limit_at_boundary(self):
        self.assertEqual(loads_bounded(b"{}" + b" " * (MAX_INPUT_BYTES - 2)), {})
        with self.assertRaisesRegex(TypedDataError, "bytes"):
            loads_bounded(b"{}" + b" " * (MAX_INPUT_BYTES - 1))

    def test_oversize_file_rejected_before_read(self):
        path = self.put("oversize.json", b" " * (MAX_INPUT_BYTES + 1))
        with self.assertRaisesRegex(TypedDataError, "bytes"):
            load_workspace_json(path)

    def test_duplicate_keys_at_any_depth(self):
        for raw in (b'{"x":1,"x":2}', b'{"message":{"x":1,"x":2}}'):
            with self.subTest(raw=raw), self.assertRaisesRegex(TypedDataError, "duplicate"):
                loads_bounded(raw)

    def test_nonfinite_float_and_exponent_rejected(self):
        for raw in (b"NaN", b"Infinity", b"-Infinity", b"1.0", b"1e3", b"1e99999"):
            with self.subTest(raw=raw), self.assertRaises(TypedDataError):
                loads_bounded(raw)

    def test_bad_unicode_and_bad_json(self):
        for raw in (b'"\xff"', b'"\\ud800"', b'{"x":', b'{]'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                loads_bounded(raw)

    def test_depth_scanned_before_decoder(self):
        self.assertEqual(loads_bounded(b"[" * MAX_DEPTH + b"]" * MAX_DEPTH),
                         json.loads("[" * MAX_DEPTH + "]" * MAX_DEPTH))
        with self.assertRaisesRegex(TypedDataError, "nesting"):
            loads_bounded(b"[" * (MAX_DEPTH + 1) + b"]" * (MAX_DEPTH + 1))

    def test_brackets_and_escaped_quotes_in_strings_do_not_count(self):
        text = '[{"\\' * 100
        self.assertEqual(loads_bounded(json.dumps(text).encode()), text)

    def test_node_and_api_text_bounds(self):
        validate_tree([True] * (MAX_NODES - 1))
        with self.assertRaisesRegex(TypedDataError, "node"):
            validate_tree([True] * MAX_NODES)
        with self.assertRaisesRegex(TypedDataError, "byte"):
            validate_tree("x" * (MAX_INPUT_BYTES + 1))

    def test_cyclic_api_values_and_nonstring_keys_rejected(self):
        cycle = []
        cycle.append(cycle)
        for value in (cycle, {1: "x"}, 1.0, float("nan"), 1 << 256):
            with self.subTest(kind=type(value)), self.assertRaises(TypedDataError):
                validate_tree(value)
        shared = {"x": 1}
        validate_tree([shared, shared])  # shared is not cyclic

    def test_outside_and_parent_paths_rejected_without_opening(self):
        for path in (Path.cwd().parent / "outside.json", "../outside.json",
                     "line-4/../outside.json"):
            with self.subTest(path=path), self.assertRaises(TypedDataError):
                load_workspace_json(path)

    def test_hidden_paths_rejected(self):
        path = self.put(".hidden.json", b"{}")
        with self.assertRaisesRegex(TypedDataError, "hidden"):
            load_workspace_json(path)

    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW"), "POSIX file safety")
    def test_file_and_directory_symlinks_rejected(self):
        target = self.put("target.json", b"{}")
        file_link = self.folder / "file-link.json"
        file_link.symlink_to(target)
        directory_link = self.folder / "dir-link"
        directory_link.symlink_to(self.folder, target_is_directory=True)
        for path in (file_link, directory_link / "target.json"):
            with self.subTest(path=path), self.assertRaises(OSError):
                load_workspace_json(path)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX FIFO")
    def test_fifo_refused_without_blocking(self):
        path = self.folder / "fifo.json"
        os.mkfifo(path)
        with self.assertRaisesRegex(TypedDataError, "regular"):
            load_workspace_json(path)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(HERE / "typed_digest.py"),
                               *map(str, args)], capture_output=True, text=True, timeout=10)

    def test_cli_match_and_mismatch(self):
        matched = self.run_cli(EXAMPLE, "--expect", EXPECTED)
        self.assertEqual(matched.returncode, 0, matched.stderr)
        self.assertTrue(json.loads(matched.stdout)["matchesExpected"])
        other_digest = "0x" + keccak256(b"different digest").hex()
        mismatch = self.run_cli(EXAMPLE, "--expect", other_digest)
        self.assertEqual(mismatch.returncode, 1, mismatch.stderr)
        self.assertFalse(json.loads(mismatch.stdout)["matchesExpected"])

    def test_cli_rejection_no_traceback_or_success_output(self):
        for raw in (b'{"x":1,"x":2}', b'"\\ud800"', b"[" * 2000,
                    b" " * (MAX_INPUT_BYTES + 1)):
            path = self.put("invalid.json", raw)
            rejected = self.run_cli(path)
            self.assertEqual(rejected.returncode, 2, rejected.stderr)
            self.assertEqual(rejected.stdout, "")
            self.assertNotIn("Traceback", rejected.stderr)


class EncodingBoundaryTests(unittest.TestCase):
    def encoder(self):
        return Encoder({"EIP712Domain": [], "Data": []})

    def test_signed_and_unsigned_limits_and_sign_extension(self):
        e = self.encoder()
        self.assertEqual(e.value_word("int8", -128), b"\xff" * 31 + b"\x80")
        self.assertEqual(e.value_word("int256", -(1 << 255)), b"\x80" + b"\0" * 31)
        self.assertEqual(e.value_word("uint256", (1 << 256) - 1), b"\xff" * 32)
        self.assertEqual(e.value_word("uint8", "0xff"), b"\0" * 31 + b"\xff")
        for kind, value in (("int8", -129), ("int8", 128), ("uint8", -1),
                            ("uint8", 256), ("uint256", True), ("uint256", "1e3")):
            with self.subTest(kind=kind, value=value), self.assertRaises(TypedDataError):
                e.value_word(kind, value)

    def test_bytes_address_boolean_encoding(self):
        e = self.encoder()
        self.assertEqual(e.value_word("bytes2", "0x1234"), b"\x12\x34" + b"\0" * 30)
        token = load_workspace_json(EXAMPLE)["message"]["token"]
        self.assertEqual(e.value_word("address", token), b"\0" * 12 + bytes.fromhex(token[2:]))
        self.assertEqual(e.value_word("bool", True), b"\0" * 31 + b"\1")
        for kind, value in (("bytes2", "0x123"), ("bytes2", "0x12"),
                            ("bool", 1), ("address", "0x1234")):
            with self.subTest(kind=kind), self.assertRaises(TypedDataError):
                e.value_word(kind, value)

    def test_empty_dynamic_and_nested_fixed_arrays(self):
        e = self.encoder()
        empty = bytes.fromhex("c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470")
        for kind, value in (("bytes", "0x"), ("string", ""), ("uint8[]", [])):
            self.assertEqual(e.value_word(kind, value), empty)
        first = keccak256(b"\0" * 31 + b"\1" + b"\0" * 31 + b"\2")
        second = keccak256(b"\0" * 31 + b"\3" + b"\0" * 31 + b"\4")
        self.assertEqual(e.value_word("uint8[2][2]", [[1, 2], [3, 4]]),
                         keccak256(first + second))

    def test_recursive_type_with_finite_values(self):
        data = {"types": {"EIP712Domain": [], "Node": [{"name": "children", "type": "Node[]"}]},
                "primaryType": "Node", "domain": {}, "message": {"children": [{"children": []}]}}
        result = digest(data)
        self.assertEqual(result["typeEncoding"], "Node(Node[] children)")
        self.assertEqual(len(result["digest"]), 66)

    def test_types_and_fields_bounded(self):
        for types in ({"EIP712Domain": [], **{f"T{i}": [] for i in range(MAX_TYPES)}},
                      {"EIP712Domain": [], "Data": [{"name": f"f{i}", "type": "bool"}
                                                        for i in range(MAX_FIELDS + 1)]}):
            with self.assertRaises(TypedDataError):
                Encoder(types)

    def test_invalid_types_and_deep_array_types_rejected(self):
        for kind in ("uint", "int", "uint7", "uint08", "bytes0", "bytes33", "Missing",
                     "uint8[0]", "uint8[01]", "uint8" + "[]" * (MAX_ARRAY_DIMENSIONS + 1)):
            with self.subTest(kind=kind), self.assertRaises(TypedDataError):
                Encoder({"EIP712Domain": [], "Data": [{"name": "x", "type": kind}]})

    def test_type_field_order_changes_digest(self):
        data = load_workspace_json(EXAMPLE)
        changed = copy.deepcopy(data)
        changed["types"]["TokenNote"].reverse()
        self.assertNotEqual(digest(data)["digest"], digest(changed)["digest"])

    def test_encoder_owns_schema_snapshot_when_caching(self):
        types = {"EIP712Domain": [], "Data": [{"name": "value", "type": "uint8"}]}
        encoder = Encoder(types)
        original = encoder.struct_hash("Data", {"value": 7})
        types["Data"][0]["type"] = "uint256"
        types["Data"].append({"name": "extra", "type": "bool"})
        self.assertEqual(encoder.type_encoding("Data"), "Data(uint8 value)")
        self.assertEqual(encoder.struct_hash("Data", {"value": 7}), original)


if __name__ == "__main__":
    unittest.main()
