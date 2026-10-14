"""Offline tests for ordered handoffs, reusable from the repository root."""
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("checker", HERE.parent / "json-contract/check.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class Ordered(unittest.TestCase):
    def check(self, doc, contract):
        return checker.validate(doc, checker.prepare(contract))

    def test_real_inherited_record(self):
        self.assertEqual(self.check(checker.load("dist/line-2/01.json"),
                                   checker.load(str(HERE / "record.strict.contract.json"))), [])

    def test_trait_value_and_order(self):
        doc = checker.load("dist/line-2/01.json")
        contract = checker.load(str(HERE / "record.strict.contract.json"))
        doc["attributes"][0]["value"] = "Wrong cave"
        doc["attributes"][2]["value"] = True
        doc["attributes"][3], doc["attributes"][4] = doc["attributes"][4], doc["attributes"][3]
        self.assertEqual({e["path"] for e in self.check(doc, contract)},
                         {"/attributes/0/value", "/attributes/2/value",
                          "/attributes/3/trait_type", "/attributes/4/trait_type"})

    def test_handoff(self):
        c = checker.load(str(HERE / "handoff.contract.json"))
        doc = checker.load(str(HERE / "handoff.example.json"))
        self.assertFalse(self.check(doc, c))
        doc["checks"][0] = [False, "yes", -1]
        self.assertEqual({e["path"] for e in self.check(doc, c)},
                         {"/checks/0/0", "/checks/0/1", "/checks/0/2"})

    def test_prefix_does_not_require_presence(self):
        self.assertFalse(self.check([], {"type": "array", "prefixItems": [{"type": "string"}]}))
        self.assertTrue(self.check([], {"type": "array", "minItems": 1,
                                      "prefixItems": [{"type": "string"}]}))

    def test_items_checks_only_tail(self):
        c = {"type": "array", "prefixItems": [{"type": "string"}], "items": {"type": "integer"}}
        self.assertFalse(self.check(["ok", 3, 4], c))
        self.assertEqual([e["path"] for e in self.check(["ok", "bad"], c)], ["/1"])

    def test_empty_prefix_retains_items(self):
        c = {"type": "array", "prefixItems": [], "items": {"type": "integer"}}
        self.assertTrue(self.check(["bad"], c))

    def test_unconstrained_tail(self):
        self.assertFalse(self.check(["ok", None, {}],
                                   {"type": "array", "prefixItems": [{"type": "string"}]}))

    def test_uniqueness_numeric_and_boolean(self):
        c = {"type": "array", "uniqueItems": True}
        self.assertFalse(self.check([True, 1, False, 0], c))
        self.assertEqual([e["path"] for e in self.check([1, 1.0, 1], c)], ["/1", "/2"])

    def test_uniqueness_nested(self):
        c = {"type": "array", "uniqueItems": True}
        self.assertEqual([e["path"] for e in self.check([{"a": [1], "b": 2},
                                                        {"b": 2.0, "a": [1.0]}], c)], ["/1"])
        self.assertFalse(self.check([[True], [1]], c))

    def test_uniqueness_optional(self):
        self.assertFalse(self.check([1, 1], {"type": "array", "uniqueItems": False}))

    def test_error_pointer(self):
        c = {"type": "object", "properties": {"a/b~c": {"type": "array", "uniqueItems": True}}}
        e = self.check({"a/b~c": [None, None]}, c)[0]
        self.assertEqual(e["path"], "/a~1b~0c/1")
        self.assertIn("/a~1b~0c/0", e["message"])

    def test_bad_contracts(self):
        for c in ({"type": "array", "prefixItems": {}},
                  {"type": "array", "prefixItems": [None]},
                  {"type": "array", "prefixItems": [{"type": "oops"}]},
                  {"type": "array", "uniqueItems": 1},
                  {"type": "string", "prefixItems": []},
                  {"type": "object", "uniqueItems": True}):
            with self.subTest(c=c), self.assertRaises(checker.ContractError):
                checker.prepare(c)

    def test_cli(self):
        r = subprocess.run([sys.executable, "-B", str(HERE / "check.py"),
                            str(HERE / "handoff.contract.json"), str(HERE / "handoff.example.json")],
                           capture_output=True, text=True, check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
