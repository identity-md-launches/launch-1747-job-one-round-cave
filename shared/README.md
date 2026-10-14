# Shared pieces

[RPC evidence bridge](rpc-evidence/README.md) combines line 1's capture format
and line 2's structural checker. It includes vendored standard-library code,
a real mainnet sample, an offline command and six regression tests. Copy its
folder into any workspace; no packages, network or cave records are needed for
validation. Capturing fresh evidence uses only public read RPC methods.

[Payment evidence bridge](payment-evidence/README.md) connects all four lines:
bounded RPC reads, structural contracts, settlement/net ZTO or IMD payment
verification, and offline typed-data commitments. It binds replay to an independently
supplied policy and includes real historical and fresh mainnet observations,
vendored standard-library code and 14 integration tests. Copy its folder to use it
without the cave or line folders.
