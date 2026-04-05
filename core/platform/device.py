"""设备能力封装：桥接 BotEngine 截图与点击。"""

from __future__ import annotations

from typing import Any

import numpy as np
from PIL import Image as PILImage

from core.base.button import Button
from models.farm_state import Action, ActionType


class Device:
    """提供 `Device` 的设备能力适配接口。"""

    def __init__(self, engine: Any):
        """初始化对象并准备运行所需状态。"""
        self.engine = engine
        self.rect: tuple[int, int, int, int] | None = None
        self.image: np.ndarray | None = None
        self.preview_image: PILImage.Image | None = None

    def set_rect(self, rect: tuple[int, int, int, int]):
        """设置 `rect` 参数。"""
        self.rect = rect

    def screenshot(
        self, rect: tuple[int, int, int, int] | None = None, *, prefix: str = 'farm', save: bool = False
    ) -> np.ndarray | None:
        """执行一次截图并更新 `image/preview_image`。"""
        if rect is not None:
            self.rect = rect
        if self.rect is None:
            self.image = None
            self.preview_image = None
            return None

        if save:
            image, _ = self.engine.screen_capture.capture_and_save(self.rect, prefix)
        else:
            image = self.engine.screen_capture.capture_region(self.rect)
        if image is None:
            self.image = None
            self.preview_image = None
            return None

        preview_image = self._crop_preview_image(image)
        if preview_image is None:
            self.image = None
            self.preview_image = None
            return None

        self.engine.screenshot_updated.emit(preview_image)
        cv_image = self.engine.cv_detector.pil_to_cv2(preview_image)
        self.preview_image = preview_image
        self.image = cv_image
        return cv_image

    def _crop_preview_image(self, image: PILImage.Image | None) -> PILImage.Image | None:
        """按窗口 nonclient 配置裁剪预览图。"""
        if image is None:
            return None
        platform = getattr(self.engine.config.planting, 'window_platform', 'qq')
        platform_value = platform.value if hasattr(platform, 'value') else str(platform)
        return self.engine.window_manager.crop_window_image_for_preview(image, platform_value)

    def set_image(self, image: np.ndarray | None):
        """设置 `image` 参数。"""
        self.image = image

    def click_button(self, button: Button, click_offset=0):
        """点击按钮对象（逻辑坐标）。"""
        x, y = button.location
        if isinstance(click_offset, (int, float)):
            x += int(click_offset)
            y += int(click_offset)
        elif isinstance(click_offset, (tuple, list)) and len(click_offset) == 2:
            x += int(click_offset[0])
            y += int(click_offset[1])
        return self.click_point(x, y, desc=button.name)

    def click_point(self, x: int, y: int, desc: str = 'point_click', action_type: str = ActionType.NAVIGATE):
        """点击逻辑坐标点（会映射到当前截图坐标系）。"""
        if not self.engine.action_executor:
            return False
        if self.engine._is_cancel_requested():
            return False

        rel_x, rel_y = self.engine.resolve_live_click_point(int(x), int(y))
        action = Action(
            type=str(action_type),
            click_position={'x': int(rel_x), 'y': int(rel_y)},
            priority=0,
            description=str(desc or 'device_click'),
        )
        result = self.engine.action_executor.execute_action(action)
        return bool(result.success)

    def _relative_to_absolute(self, x: int, y: int) -> tuple[int, int] | None:
        """将逻辑坐标转换为屏幕绝对坐标。"""
        if not self.engine.action_executor:
            return None
        rel_x, rel_y = self.engine.resolve_live_click_point(int(x), int(y))
        return self.engine.action_executor.relative_to_absolute(int(rel_x), int(rel_y))

    def drag_down_point(self, x: int, y: int, duration: float = 0.05) -> bool:
        """移动到目标点后按下鼠标，用于拖拽起手。"""
        if self.engine._is_cancel_requested():
            return False
        pos = self._relative_to_absolute(int(x), int(y))
        if pos is None:
            return False
        abs_x, abs_y = pos
        if not self.engine.action_executor.move_abs(abs_x, abs_y, duration=duration):
            return False
        return self.engine.action_executor.mouse_down()

    def drag_move_point(self, x: int, y: int, duration: float = 0.1) -> bool:
        """拖拽中移动到目标点。"""
        if self.engine._is_cancel_requested():
            return False
        pos = self._relative_to_absolute(int(x), int(y))
        if pos is None:
            return False
        abs_x, abs_y = pos
        return self.engine.action_executor.move_abs(abs_x, abs_y, duration=duration)

    def drag_up(self) -> bool:
        """结束拖拽，释放鼠标。"""
        if not self.engine.action_executor:
            return False
        return self.engine.action_executor.mouse_up()

    def long_click_point(self, x: int, y: int, seconds: float):
        """长按逻辑坐标点。"""
        ok = self.click_point(int(x), int(y), desc=f'long_click({seconds:.1f}s)')
        if ok:
            self.sleep(seconds)
        return ok

    def sleep(self, seconds: float):
        """执行 `sleep` 相关处理。"""
        return self.engine._sleep_interruptible(float(seconds))

    def stuck_record_add(self, _button):
        """执行 `stuck record add` 相关处理。"""
        return None

    def stuck_record_clear(self):
        """执行 `stuck record clear` 相关处理。"""
        return None

    def click_record_clear(self):
        """执行点击动作并返回是否成功。"""
        return None

    def app_is_running(self) -> bool:
        """执行 `app is running` 相关处理。"""
        return not self.engine._is_cancel_requested()

    def get_orientation(self):
        """获取 `orientation` 信息。"""
        return 0


