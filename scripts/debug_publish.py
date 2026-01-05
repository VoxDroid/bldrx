# ensure workspace package path is first
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
from bldrx.registry import Registry  # noqa: E402

p = Path(sys.argv[1])
print("src exists:", p.exists())
r = Registry()
try:
    meta = r.publish(
        p,
        name=sys.argv[2],
        version=sys.argv[3],
        description="A test",
        tags=["test", "example"],
    )
    import json

    print(json.dumps(meta, indent=2))
except Exception as e:
    import traceback

    print("ERROR", type(e).__name__, e)
    traceback.print_exc()
