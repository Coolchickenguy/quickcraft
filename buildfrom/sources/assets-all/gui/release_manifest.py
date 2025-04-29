import json
from assets_root import assets_root
import os
with open(os.path.join(assets_root,"release_manifest.json")) as f:
    release_manifest = json.load(f)