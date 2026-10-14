#!/usr/bin/env python3
"""Replay public token-payment evidence against a separate policy, offline."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, HERE / relative)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


contracts = module('payment_contracts', 'vendor/json_contract.py')
typed = module('payment_typed', 'vendor/typed_digest.py')
witness = module('payment_witness', 'vendor/payment-witness/witness.py')


def load(path):
    # Line 4's no-follow regular-file reader also bounds depth, size and values.
    return typed.load_workspace_json(path)


def validate(value, filename):
    contract = contracts.prepare(load(HERE / filename))
    errors = contracts.validate(value, contract)
    if errors:
        raise ValueError(json.dumps(errors, separators=(',', ':')))


def policy(value):
    validate(value, 'policy.contract.json')
    witness.settlement.hash32(value['tx'])
    witness.address(value['recipient'])
    witness.positive(value['minimum_raw'])
    return value


def commitment(sample, expected):
    """A reproducible content commitment, never a signature or token permit."""
    encoded = json.dumps(sample, sort_keys=True, separators=(',', ':'),
                         ensure_ascii=False, allow_nan=False).encode('utf-8')
    transcript_hash = '0x' + hashlib.sha256(encoded).hexdigest()
    fields = [('transactionHash', 'bytes32'), ('token', 'address'),
              ('recipient', 'address'), ('minimumRaw', 'uint256'),
              ('confirmations', 'uint256'), ('requireFinalized', 'bool'),
              ('transcriptHash', 'bytes32')]
    data = {
        'types': {
            'EIP712Domain': [{'name': n, 'type': t} for n, t in
                             [('name', 'string'), ('version', 'string'), ('chainId', 'uint256')]],
            'PaymentEvidence': [{'name': n, 'type': t} for n, t in fields]},
        'primaryType': 'PaymentEvidence',
        'domain': {'name': 'Read-only Payment Evidence', 'version': '1', 'chainId': 1},
        'message': {
            'transactionHash': expected['tx'].lower(),
            'token': witness.TOKENS[expected['token']],
            'recipient': expected['recipient'].lower(),
            'minimumRaw': expected['minimum_raw'],
            'confirmations': expected['confirmations'],
            'requireFinalized': expected['finalized'],
            'transcriptHash': transcript_hash}}
    return data, typed.digest(data)


def check(sample, expected, expect_digest=None):
    typed.validate_tree(sample)
    typed.validate_tree(expected)
    validate(sample, 'transcript.contract.json')
    policy(expected)
    # Never let an edited transcript lower the worker's independent policy.
    if not contracts.same(sample['policy'], expected):
        raise ValueError('transcript /policy differs from the independently supplied policy')
    for read in sample['reads']:
        if set(read) != {'method', 'params', 'result'}:
            raise ValueError('each read needs exactly method, params and result')
    replay = witness.Replay(sample['reads'])
    report = witness.verify(replay, **expected)
    if replay.index != len(replay.reads):
        raise ValueError('unused transcript reads')
    data, digest = commitment(sample, expected)
    matches = None
    if expect_digest is not None:
        matches = typed.parse_hex(expect_digest, 32).hex() == digest['digest'][2:]
    return {
        'validEvidence': True,
        'policyMatched': True,
        'accepted': report['accepted'] and matches is not False,
        'evidenceMode': 'offline historical RPC observations',
        'providerAuthenticated': False,
        'settlementAndPayment': report,
        'typedData': data,
        'commitment': digest,
        'matchesExpectedDigest': matches}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('transcript')
    parser.add_argument('policy', help='independently chosen payment policy')
    parser.add_argument('--expect-digest', help='optional previously recorded commitment')
    args = parser.parse_args()
    try:
        result = check(load(args.transcript), load(args.policy), args.expect_digest)
        print(json.dumps(result, indent=2))
        return 0 if result['accepted'] else 1
    except (ValueError, OSError, TypeError, KeyError, RecursionError) as exc:
        print(json.dumps({'accepted': False, 'validEvidence': False, 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
