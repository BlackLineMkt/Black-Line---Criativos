import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_no_args_exits_with_usage():
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "bl_gerar.py")],
        capture_output=True, text=True
    )
    assert result.returncode == 1
    assert "Uso:" in result.stderr or "Uso:" in result.stdout
