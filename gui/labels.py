"""GUI 文案配置读取。"""

from __future__ import annotations

import json
from functools import lru_cache

from utils.app_paths import ensure_user_configs, resolve_config_file


@lru_cache(maxsize=1)
def load_ui_labels() -> dict:
    """加载统一 UI 文案配置。"""
    ensure_user_configs()
    labels_path = resolve_config_file('ui_labels.json', prefer_user=True)
    if not labels_path.exists():
        return {}
    try:
        data = json.loads(labels_path.read_text(encoding='utf-8'))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}

