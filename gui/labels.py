"""GUI 文案配置读取。"""

from __future__ import annotations

import json
from functools import lru_cache

from utils.app_paths import ensure_user_configs, resolve_config_file


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for key, value in (override or {}).items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


@lru_cache(maxsize=1)
def load_ui_labels() -> dict:
    """加载统一 UI 文案配置。"""
    ensure_user_configs()
    bundled_path = resolve_config_file('ui_labels.json', prefer_user=False)
    user_path = resolve_config_file('ui_labels.json', prefer_user=True)

    bundled_data: dict = {}
    if bundled_path.exists():
        try:
            data = json.loads(bundled_path.read_text(encoding='utf-8'))
            bundled_data = data if isinstance(data, dict) else {}
        except Exception:
            bundled_data = {}

    user_data: dict = {}
    if user_path.exists():
        try:
            data = json.loads(user_path.read_text(encoding='utf-8'))
            user_data = data if isinstance(data, dict) else {}
        except Exception:
            user_data = {}

    if not bundled_data and not user_data:
        return {}

    if bundled_data and user_data:
        return _deep_merge(bundled_data, user_data)
    if user_data:
        return user_data
    return bundled_data
