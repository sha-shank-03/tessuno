#!/usr/bin/env python3
import argparse,sys
from library import load_catalog, Invalid, publication_gate
p=argparse.ArgumentParser();p.add_argument('--publication',action='store_true');a=p.parse_args()
try:
 records=load_catalog()
 if a.publication:publication_gate(records)
 print(f'PASS: {len(records)} objects; schema, native skill, scopes, references and paths checked. Compatibility remains declared-only.')
except Invalid as e:
 print(f'FAIL: {e}',file=sys.stderr);sys.exit(1)
