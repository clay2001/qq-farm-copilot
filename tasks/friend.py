"""独立好友任务。"""

from __future__ import annotations

from core.engine.task.registry import TaskResult
from core.ui.page import page_main
from tasks.base import TaskBase
from tasks.farm_friend import TaskFarmFriend


class TaskFriend(TaskBase):
    """封装 `TaskFriend` 任务的执行入口与步骤。"""

    def __init__(self, engine, ui):
        """初始化对象并准备运行所需状态。"""
        super().__init__(engine, ui)
        self._friend = TaskFarmFriend(engine=engine, ui=ui)

    def run(self, rect: tuple[int, int, int, int]) -> TaskResult:
        """执行好友任务并返回调度结果。"""
        self.engine._clear_screen(rect)
        self.ui.ui_ensure(page_main, confirm_wait=0.5)

        out = self._friend.run(rect=rect, features=self.get_features('friend'))
        return self.ok(actions=list(out.actions))
