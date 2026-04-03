# TODO - 页面跳转与状态机改造计划

## 目标
将当前“全量扫描 + 业务内跳转”的流程，改造成“页面图 + 导航器 + 全局兜底 + 状态分发”，提升稳定性与性能。

## 阶段 1：页面图（Page Graph）
- [ ] 新建 `core/page_graph.py`
- [ ] 定义页面节点：`MAIN / TASK_POPUP / SHOP / BUY_CONFIRM / PLOT_MENU / SEED_SELECT / FRIEND / UNKNOWN`
- [ ] 定义页面跳转边：点击任务、打开商店、确认购买、关闭弹窗、回家等
- [ ] 提供查询接口：给定当前页与目标页，返回下一跳动作

## 阶段 2：页面识别器（替代单纯场景枚举）
- [ ] 在 `core/scene_detector.py` 增加 `resolve_page(detections, image) -> PageId`
- [ ] 保留“两阶段识别”（严格 -> 回退）
- [ ] 保留“连续帧确认”
- [ ] 增加页面识别超时机制（超时回 `UNKNOWN`）

## 阶段 3：导航器（Navigator）
- [ ] 新建 `core/navigator.py`
- [ ] 实现 `get_current_page()`
- [ ] 实现 `goto(target_page, timeout=...)`
- [ ] 实现 `ensure(target_page)`
- [ ] 每次跳转点击后加入确认等待（confirm wait）
- [ ] 超时重试与失败返回

## 阶段 4：全局弹窗兜底
- [ ] 新建 `core/ui_guard.py`（或 `core/recovery.py`）
- [ ] 在主循环统一执行 `handle_global_popups()`
- [ ] 将通用关闭逻辑从各策略下沉到全局层
- [ ] 统一处理未知可恢复页面（例如返回主页、关闭弹窗）

## 阶段 5：策略契约化（前置/后置条件）
- [ ] 为策略动作声明 `requires_page`
- [ ] 为关键动作声明 `target_page_after_action`
- [ ] 执行标准流程：
  1. `navigator.ensure(requires_page)`
  2. 执行业务动作
  3. 校验后置页面或锚点

## 阶段 6：节流与去抖（全局）
- [ ] 增加 `ActionCooldown`（动作最小触发间隔）
- [ ] 增加 `TemplateNoiseGuard`（高噪声模板临时降权）
- [ ] 增加 `PageTransitionBudget`（单次跳转最大点击次数）

## 阶段 7：主循环重构为状态分发
- [ ] 将 `check_farm()` 从“最多 50 轮扫描”改为状态驱动分发
- [ ] 新流程：`tick -> global_guard -> resolve_page -> dispatch(page_handler)`
- [ ] 页面处理器最小化：MAIN / SHOP / BUY_CONFIRM / POPUP / FRIEND

## 建议落地顺序
1. 页面图 + PageId（不改业务）
2. Navigator 最小可运行（先接 MAIN/POPUP/SHOP/BUY_CONFIRM）
3. 全局弹窗兜底
4. 迁移 `task/plant/sell` 三个策略到 Navigator
5. 重构 `check_farm()` 为状态分发

## 验收指标
- [ ] 误跳转次数显著下降（日志可量化）
- [ ] 单轮平均处理耗时下降
- [ ] 停止/暂停后残留动作减少
- [ ] 关键流程（任务、买种、出售）可稳定往返主页
