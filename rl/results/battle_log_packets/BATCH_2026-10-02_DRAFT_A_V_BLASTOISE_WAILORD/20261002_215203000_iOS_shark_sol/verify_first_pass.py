import importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('batch_validator',P.parent/'validate_packet.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
result=module.validate(P)
(P/'FIRST_PASS_STRUCTURAL_CHECK.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
