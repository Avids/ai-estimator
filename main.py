import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from guild_ai.gui import run
if __name__ == '__main__':
    run()
