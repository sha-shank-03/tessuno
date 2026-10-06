#!/usr/bin/env python3
import argparse,sys
from library import load_catalog, Invalid, publication_gate, project_identity_check
p=argparse.ArgumentParser();p.add_argument('--publication',action='store_true')
p.add_argument('--project-policy',action='store_true',help='Check original Tessuno maintainer/license declarations and approved license bytes; not generic SPDX validation')
a=p.parse_args()
try:
 records=load_catalog()
 if a.project_policy:project_identity_check(records)
 if a.publication:publication_gate(records)
 print(f'PASS: {len(records)} objects; schema, native skill, scopes, references and paths checked. Compatibility remains declared-only.')
 if a.project_policy:print('PASS: original-project maintainer/license declarations and approved Apache-2.0 text match. Identity authentication and comprehensive license validation remain unavailable.')
except Invalid as e:
 print(f'FAIL: {e}',file=sys.stderr);sys.exit(1)
