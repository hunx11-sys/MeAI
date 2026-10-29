# API 약속 점검 : 모의 서버(src/api/mock.js)가 내보내는 응답이 docs/openapi.yaml 의 모양과 맞는지 본다.
# 쓰는 법 : python3 home_nudge/tools/check_contract.py   (필요 : pip install openapi-spec-validator · node)
import json, os, subprocess, sys
from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename
from openapi_schema_validator import OAS30Validator
from referencing import Registry, Resource

HERE = os.path.dirname(os.path.abspath(__file__))
spec, _ = read_from_filename(os.path.join(HERE, '..', 'docs', 'openapi.yaml'))
validate(spec)
res = Resource.from_contents(spec, default_specification=__import__('referencing.jsonschema', fromlist=['DRAFT4']).DRAFT4)
reg = Registry().with_resource('spec', res)
dump = json.loads(subprocess.check_output(['node', os.path.join(HERE, 'dump_mock.js')]))
fail = 0
for key, val in dump.items():
    name = key.split('_')[0]
    schema = {'$ref': 'spec#/components/schemas/' + name}
    errs = sorted(OAS30Validator(schema, registry=reg).iter_errors(val), key=lambda e: list(e.path))
    if errs:
        fail += 1
        print('✗', key, '→', name)
        for e in errs[:6]: print('   ', '/'.join(map(str, e.path)), ':', e.message[:160])
    else: print('✓', key, '→', name)
print('\n실패 %d' % fail if fail else '\n모두 맞음')
sys.exit(1 if fail else 0)
