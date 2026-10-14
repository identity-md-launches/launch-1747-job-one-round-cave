#!/usr/bin/env python3
"""Capture a public, bounded payment-policy transcript; stdout only."""
import argparse
import json
import sys

from check import check, load, module, policy, witness

snapshot = module('payment_snapshot', 'vendor/rpc_snapshot.py')


class PublicReads:
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def call(self, method, params):
        # Line 1 checks parameters, envelopes, duplicate keys, byte limits and
        # disallows redirects and proxy environment discovery. No write method.
        _, answer = snapshot.rpc_call(self.endpoint, method, params, 20)
        return answer['result']


def capture(expected, endpoint):
    policy(expected)
    recorder = witness.Recorder(PublicReads(endpoint))
    witness.verify(recorder, **expected)
    sample = {'version': 1, 'policy': expected, 'reads': recorder.reads}
    # Prove the emitted transcript is replayable before handing it off.
    check(sample, expected)
    encoded = json.dumps(sample, indent=2) + '\n'
    if len(encoded.encode('utf-8')) > 65536:
        raise ValueError('transcript exceeds the offline reader limit; not emitted')
    return encoded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('policy')
    parser.add_argument('--rpc-url', choices=[snapshot.DEFAULT_RPC, 'https://eth.drpc.org'],
                        default=snapshot.DEFAULT_RPC)
    args = parser.parse_args()
    try:
        sys.stdout.write(capture(load(args.policy), args.rpc_url))
        return 0
    except (ValueError, OSError, TypeError, KeyError, RecursionError,
            snapshot.SnapshotError) as exc:
        print('payment-evidence capture: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
