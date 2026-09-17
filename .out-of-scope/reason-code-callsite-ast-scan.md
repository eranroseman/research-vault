# Reason-code call-site AST scan

This project will not infer the reason-code vocabulary from the syntax of
`inbox.append_entry` call sites.

## Why this is out of scope

Production writers generally pass a reason through shared `Outcome` objects,
wrapper functions, or validated user input. An AST scan of the immediate
`append_entry` arguments therefore cannot derive the set of reasons the system
can emit. It would cover a convenient literal subset while presenting itself
as a placement guarantee.

The failure that motivated the proposal already has a direct guard:
`test_evidence_conventions_accounts_for_every_reason_code` requires the
reason-code table and its explicitly named exemptions to account for the live
`REASON_CODES` registry exactly once. The post-slice queue also owns the
stronger long-term option of removing duplicated prose enumerations in favor
of registry-backed presentation. Those mechanisms test the contract itself;
the rejected call-site scan would test an incomplete proxy.

This decision does not reject reason-code governance, registry-backed
documentation, or focused checks over a concrete writer interface. It rejects
only a repository-wide claim derived from `append_entry` argument syntax.

## Prior requests

- [#26 — Reason-code placement: AST scan of inbox.append_entry reason arguments](https://github.com/eranroseman/research-vault/issues/26)
