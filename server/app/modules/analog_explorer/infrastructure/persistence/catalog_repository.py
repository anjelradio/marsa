"""
Repository loading the versioned scientific catalog (`data/catalog/regions.json`),
provenance manifest (`data/manifest.json`), and processed Mars MCD v6.2 layers
(`data/processed/mars_mcd_ls105.json`).
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[6]
DATA_DIR = ROOT_DIR / "data"
CATALOG_FILE = DATA_DIR / "catalog" / "regions.json"
MANIFEST_FILE = DATA_DIR / "manifest.json"
MARS_MCD_FILE = DATA_DIR / "processed" / "mars_mcd_ls105.json"


class CatalogRepository:
    def __init__(
        self,
        catalog_path: Path = CATALOG_FILE,
        manifest_path: Path = MANIFEST_FILE,
        mars_mcd_path: Path = MARS_MCD_FILE,
    ) -> None:
        self._catalog_path = catalog_path
        self._manifest_path = manifest_path
        self._mars_mcd_path = mars_mcd_path

    def get_all_regions(self) -> list[dict[str, Any]]:
        return _load_json_list(str(self._catalog_path))

    def get_manifest(self) -> dict[str, Any]:
        return _load_json_dict(str(self._manifest_path))

    def get_mars_mcd_summary(self) -> dict[str, Any]:
        return _load_json_dict(str(self._mars_mcd_path))

    def get_region_by_id(self, region_id: str) -> dict[str, Any] | None:
        for region in self.get_all_regions():
            if region["id"] == region_id:
                return region
        return None

    def get_targets(self, body: str | None = None) -> list[dict[str, Any]]:
        targets = [r for r in self.get_all_regions() if r["body"] in ("mars", "moon")]
        if body:
            b_lower = body.lower()
            targets = [r for r in targets if r["body"] == b_lower]
        return targets

    def get_sites(self, body: str = "earth") -> list[dict[str, Any]]:
        b_lower = body.lower()
        return [r for r in self.get_all_regions() if r["body"] == b_lower]


@lru_cache(maxsize=8)
def _load_json_list(path_str: str) -> list[dict[str, Any]]:
    path = Path(path_str)
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=8)
def _load_json_dict(path_str: str) -> dict[str, Any]:
    path = Path(path_str)
    return json.loads(path.read_text(encoding="utf-8"))
