# Qt 视频桌面应用自动化测试

这是第一版 macOS 自动化测试工程骨架，目标是覆盖 Qt 视频处理应用的 P0 核心回归：

- 启动应用
- 导入视频
- MP4 转 MOV
- MOV 转 MP4
- MP4 视频压缩
- MP4 提取音频
- MP4 转 GIF

## 方案

- UI 自动化：Appium + mac2 driver
- 测试框架：pytest
- 媒体校验：ffprobe
- 报告：pytest-html

## 环境准备

安装 Python 依赖：

```bash
pip install -r requirements.txt
```

安装 Appium mac2 driver：

```bash
appium driver install mac2
```

确认 ffprobe 可用：

```bash
ffprobe -version
```

macOS 需要给 Terminal、Appium 或执行测试的 IDE 开启辅助功能权限：

```text
System Settings -> Privacy & Security -> Accessibility
```

## 配置应用信息

复制示例配置：

```bash
cp config/test_config.example.json config/test_config.json
```

修改 `config/test_config.json`：

```json
{
  "app": {
    "bundle_id": "com.yourcompany.VideoApp",
    "app_path": "/Applications/YourVideoApp.app"
  },
  "selectors": {
    "main_window": "mainWindow",
    "import_button": "btnImport"
  }
}
```

`selectors` 中的值应替换为 Qt 控件真实的 `objectName` 或能被 macOS accessibility 识别的名称。

## 执行测试

推荐使用统一脚本执行。脚本会自动检查 Appium 是否已运行；如果没有运行，会后台启动 Appium，测试结束后再自动停止它。

只跑工具层单元测试：

```bash
./run_desktop_auto.sh unit
```

执行 macOS 桌面 UI 冒烟测试：

```bash
./run_desktop_auto.sh smoke
```

执行核心回归入口测试：

```bash
./run_desktop_auto.sh core
```

报告输出：

- `reports/smoke.html`
- `reports/core.html`
- `reports/appium.log`

也可以手动执行底层命令：

```bash
python3 -m pytest tests/unit -q
```

启动 Appium：

```bash
appium --base-path /
```

执行 macOS 桌面 UI 冒烟测试：

```bash
RUN_DESKTOP_E2E=1 python3 -m pytest tests/e2e -m smoke --html=reports/smoke.html
```

执行核心回归：

```bash
RUN_DESKTOP_E2E=1 python3 -m pytest tests/e2e -m core --html=reports/core.html
```

## 当前状态

当前工程已完成：

- 路径管理工具
- 输出文件断言工具
- ffprobe 结果解析工具
- macOS Appium driver 创建入口
- 页面对象基础结构
- 7 条 P0 UI 用例入口
- E2E 失败截图和 page source 采集
- pytest marker 配置
- 示例配置文件

需要接入真实应用后继续补充：

- 测试账号登录状态
- 文件导入对话框操作
- 各功能固定参数选择
- 输出文件路径与命名规则
- 完整媒体属性断言

## 已知前置条件

当前 `config/test_config.json` 指向本机 VideoBee 调试包。真实 E2E 进入视频转换、压缩、音频提取或 GIF 工作流时，如果应用弹出“请先在浏览器中完成登录后再继续”，测试会失败并提示先完成测试账号登录。这属于环境/账号前置条件未满足，不是控件定位失败。

失败时会保存：

- `screenshots/<test-id>.png`
- `logs/<test-id>.xml`
