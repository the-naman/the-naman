"""Rebuilds everything that is committed: assets/ (SVGs) and README.md, from config/profile.yml.

    pip install pyyaml==6.0.3 && python scripts/build_all.py

The live parts (dist/: activity, trophies, snake, dashboard) are built by .github/workflows/profile.yml.
"""

import build_readme
import build_readme_assets

if __name__ == "__main__":
    build_readme_assets.main()
    build_readme.main()
