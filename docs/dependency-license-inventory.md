# Factual pinned dependency license inventory

Recorded 2026-10-06 from the unchanged `requirements-dev.lock`, SHA-256 `0a27a482e9218cf597810076317aef72e30eddad2d4b8cb30ea5240b1e70ca0e`, on the PR26 source basis `30ec037426f09f014c9d60f081dac8e278af1d09` / tree `403e1739593802ff9179645409e88a7b1c8e4aaf`. This inventory records exact artifact bytes and shipped notices. It supplies no admission decision, legal compatibility assessment or account/contact authentication. Qualified publication remains blocked.

## Artifact selection and provenance

One existing cached wheel was inspected for each of the seven exact pins: five universal wheels and the CPython 3.12 macOS 11 arm64 wheels for PyYAML and rpds-py. Their hashes match the lock, and their hashes and sizes match a captured HTTP 200 PyPI exact-release JSON readback. Each wheel license file is byte-identical to the license file at the upstream release tag commit linked below. Tags were resolved from the public upstream tag collections; commit URLs bind the observed bytes. No dependency was installed or executed for this inventory.

The [machine-readable inventory](dependency-license-inventory.json) records artifact URLs, complete wheel and license SHA-256 values, metadata/RECORD hashes, tags/commits, readback times, copyright text, notice-file search scope and ambiguities. Raw wheels, HTTP responses and extracted METADATA/WHEEL/RECORD receipts remain outside the repository. The repository contains seven verbatim license-text copies as documentation, not dependency implementations or binaries. The offline kit does not include this repository-only inventory or those copies.

| Exact pin | Declared wheel license field | Shipped license copy | Exact upstream release source |
| --- | --- | --- | --- |
| attrs 26.1.0 | `License-Expression: MIT` | [LICENSE](dependency-licenses/attrs/LICENSE) | [26.1.0](https://github.com/python-attrs/attrs/blob/7bfc49e9b22d5ba25b6e429524c3d49fee27cb36/LICENSE) |
| jsonschema 4.26.0 | `License-Expression: MIT` | [COPYING](dependency-licenses/jsonschema/COPYING) | [v4.26.0](https://github.com/python-jsonschema/jsonschema/blob/a7277432b0f7bcd0551f6e589d30457017125df4/COPYING) |
| jsonschema-specifications 2025.9.1 | `License-Expression: MIT` | [COPYING](dependency-licenses/jsonschema-specifications/COPYING) | [v2025.9.1](https://github.com/python-jsonschema/jsonschema-specifications/blob/3b846010c34ce254d8ced23023451d1d64de37f5/COPYING) |
| PyYAML 6.0.3 | legacy `License: MIT`; no License-Expression | [LICENSE](dependency-licenses/pyyaml/LICENSE) | [6.0.3](https://github.com/yaml/pyyaml/blob/49790e73684bebad1df05ef8d828fa12f685bffb/LICENSE) |
| referencing 0.37.0 | `License-Expression: MIT` | [COPYING](dependency-licenses/referencing/COPYING) | [v0.37.0](https://github.com/python-jsonschema/referencing/blob/944ed5a20bc5125f2349156cbdc365daac0e67e6/COPYING) |
| rpds-py 2026.6.3 | `License-Expression: MIT` | [LICENSE](dependency-licenses/rpds-py/LICENSE) | [v2026.6.3](https://github.com/crate-py/rpds/blob/7277eb681f6efd67eca1bbaa32f78d78bdc044a5/LICENSE) |
| typing_extensions 4.16.0 | `License-Expression: PSF-2.0` | [LICENSE](dependency-licenses/typing-extensions/LICENSE) | [4.16.0](https://github.com/python/typing_extensions/blob/f29cd28d8ed7642cafb1d18daf5aa41be6a5c0aa/LICENSE) |


| Selected wheel filename | SHA-256 |
| --- | --- |
| `attrs-26.1.0-py3-none-any.whl` | `c647aa4a12dfbad9333ca4e71fe62ddc36f4e63b2d260a37a8b83d2f043ac309` |
| `jsonschema-4.26.0-py3-none-any.whl` | `d489f15263b8d200f8387e64b4c3a75f06629559fb73deb8fdfb525f2dab50ce` |
| `jsonschema_specifications-2025.9.1-py3-none-any.whl` | `98802fee3a11ee76ecaca44429fda8a41bff98b00a0f2838151b113f210cc6fe` |
| `pyyaml-6.0.3-cp312-cp312-macosx_11_0_arm64.whl` | `fc09d0aa354569bc501d4e787133afc08552722d3ab34836a80547331bb5d4a0` |
| `referencing-0.37.0-py3-none-any.whl` | `381329a9f99628c9069361716891d34ad94af76e461dcb0335825aecc7692231` |
| `rpds_py-2026.6.3-cp312-cp312-macosx_11_0_arm64.whl` | `538949e262e46caa31ac01bdb3c1e8f642622922cacbabbae6a8445d9dc33eaf` |
| `typing_extensions-4.16.0-py3-none-any.whl` | `481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8` |


## What the notice texts say

The six MIT-text files contain the condition to keep the copyright and permission notices in copies or substantial portions of the software. Their originating notices are preserved in the full files: attrs names Hynek Schlawack and the attrs contributors (2015); jsonschema names Julian Berman (2013); jsonschema-specifications and referencing name Julian Berman (2022); rpds-py names Julian Berman (2023); PyYAML names Ingy döt Net (2017–2021) and Kirill Simonov (2006–2016). These are copied attribution facts, not new Tessuno copyright declarations.

The full 13,936-byte typing_extensions LICENSE is retained. Its metadata declares PSF-2.0, but the file also contains history, BeOpen, CNRI, CWI and documentation Zero-Clause BSD sections. The PSF section, clauses 2–3, states retention of its agreement/copyright notice and a brief change summary for a derivative made available to others. BeOpen clause 2 states retention of its license. CNRI clause 2 states retention of its agreement and copyright notice; its specified identifying text/URL may substitute for the Agreement, while the copyright-retention condition remains stated. CNRI clause 3 states a brief change summary for a derivative made available to others. The CWI section states copyright retention in copies, copyright/permission notices in supporting documentation, and a restriction on advertising with CWI/SMC names without permission. This records the clauses as written; it does not decide the applicability of every historical section or substitute a newly composed SPDX expression for the declared field. Preserve the full file while applicability remains unresolved.

All seven selected wheels have one non-directory entry whose basename contains LICENSE, COPYING, NOTICE or AUTHORS (case-insensitive), matching their declared License-File. No separate NOTICE file was found in that named-file search. This is not proof that no attribution can occur elsewhere in source, binaries or transitive dependencies. All 156 non-RECORD regular-file hashes and sizes in the wheel RECORD files were verified; RECORD self-rows have no hash. These checks identify bytes and do not authenticate authors or certify legal sufficiency.

## Reproduce the factual checks

Use the exact filenames and hashes above, not an installed package directory or a reconstructed wheel. Retain the exact-release PyPI JSON URLs and the upstream commit URLs in the JSON inventory. The raw response hashes and observed times distinguish those snapshots from mutable current pages.

For each selected wheel:

1. Hash the complete wheel and compare its filename, version, size and SHA-256 with the lock and exact-release PyPI file record.
2. Read METADATA, WHEEL and RECORD as ZIP data; compare normalized Name, Version, License-Expression/legacy License, License-File and wheel tags with the inventory. Verify each RECORD file hash and size, excluding its explicitly unhashed self-row.
3. Compare the copied license file with its original wheel entry and the exact-commit upstream license file byte for byte, including copyright, whitespace and the entire typing_extensions history. Hash each text and compare with the recorded value.
4. Repeat the scoped named-file search and record native extension paths. Keep missing transitive information explicit; matching the project license cannot fill that gap.

Built-in read-only inspection examples (no imports of dependency code):

```sh
shasum -a 256 /path/to/exact-selected-wheel.whl
python3 -m zipfile -l /path/to/exact-selected-wheel.whl
shasum -a 256 docs/dependency-licenses/typing-extensions/LICENSE
```

## Remaining scope

Other platform wheels and sdists permitted by the lock were not inspected. The PyYAML and rpds-py wheels contain native extensions, so a source/build-linked inventory of compiled transitive components remains an evidence task before claiming complete binary attribution. A short package license field does not establish that every compiled component uses that license. The typing_extensions historical-section applicability remains unresolved; its complete text is available for review.

None of these gaps prevents this factual source inventory. A future third-party admission/redistribution proposal still needs the owner-selected license/SPDX/per-file/dependency policy; it is not adopted here. No new agreement, CLA/DCO, account authentication, permissions, CI dispatch, deployment, foreground observation or live evaluation follows from this document. Original Tessuno licensing and all fail-closed gates remain in place.
