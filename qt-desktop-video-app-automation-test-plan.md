# Qt 桌面视频应用自动化测试执行计划

## 1. 背景与目标

本计划用于指导一个基于 Qt 的桌面端视频处理应用，在 macOS 平台上落地第一版自动化回归测试与 UI 自动化测试。

已知条件：

- 应用技术栈：Qt
- 首版运行平台：macOS
- 后续覆盖平台：Windows
- 自动化目标：回归测试 + UI 自动化
- 工具要求：免费开源方案
- 控件可测试性：Qt 控件具备稳定 `objectName`
- 视频处理底层：使用 `ffmpeg`
- 输出参数：固定
- 测试基础：已有测试账号和测试数据
- 当前状态：暂无 CI/CD
- 落地周期：一周内完成第一版
- 主要质量风险：核心功能处理结果有误

第一版目标：

> 在一周内完成一套可本地一键执行的 macOS 自动化回归流程，覆盖核心视频处理链路，能自动启动应用、导入测试视频、执行视频格式转换、视频压缩、音频提取、视频转 GIF，并使用 `ffprobe` 校验输出文件的基础媒体属性，失败时保留截图、日志和 HTML 测试报告。

## 2. 成功标准

第一版自动化测试完成后，应满足以下标准：

- 能在 macOS 测试机上本地一键执行。
- 能自动启动和关闭被测 Qt 应用。
- 能通过 UI 完成核心功能操作。
- 能执行 7 条 P0 核心回归用例。
- 每条核心用例都具备明确断言，而不是只依赖 UI 成功提示。
- 能生成 HTML 测试报告。
- 失败时能保留截图、自动化日志、应用日志和输出目录。
- 测试数据和输出目录固定，便于重复执行。
- 测试误报可定位，失败原因能区分为产品问题、脚本问题或环境问题。

第一版不包含：

- Windows 平台自动化。
- CI/CD 接入。
- 大规模兼容性测试。
- 主观视频质量评价。
- 全量异常场景覆盖。
- 性能压测和长时间稳定性测试。

## 3. 技术方案

### 3.1 推荐技术栈

| 模块 | 方案 |
|---|---|
| 测试语言 | Python |
| 测试框架 | pytest |
| UI 自动化 | Appium + mac2 driver |
| UI 兜底方案 | pyautogui |
| 控件定位 | Qt `objectName` / macOS accessibility |
| 视频属性校验 | ffprobe |
| 测试报告 | pytest-html |
| 日志 | Python logging + 应用日志收集 |
| 截图 | Appium screenshot / pyautogui screenshot |
| 测试数据 | 固定短视频样本 |

### 3.2 工具选型理由

首选 `Appium + mac2 driver`：

- 免费开源。
- 支持 macOS 桌面应用自动化。
- 能通过 accessibility 信息定位 UI 控件。
- 适合和 `pytest` 集成。
- 后续如果扩展 Windows，可以继续使用 Appium Windows driver 或切换到 pywinauto。

使用 `ffprobe` 校验结果：

- 应用底层使用 `ffmpeg`，输出参数固定。
- `ffprobe` 能客观校验格式、时长、分辨率、视频流、音频流、帧数等信息。
- 能避免“UI 提示成功但输出文件错误”的漏测。

保留 `pyautogui` 作为兜底：

- 用于处理 Appium 无法稳定操作的系统弹窗、文件选择器或特殊控件。
- 不作为主方案，避免脚本依赖坐标导致不稳定。

## 4. 自动化整体流程

标准执行流程：

```text
1. 准备 macOS 测试环境
2. 安装或更新被测 Qt 应用
3. 清理上一次测试输出目录
4. 清理或重置应用测试配置
5. 启动 Appium 服务
6. 启动被测应用
7. 等待主窗口出现
8. 导入固定测试视频
9. 选择目标处理功能
10. 设置固定输出参数
11. 启动处理任务
12. 等待任务完成
13. 校验 UI 状态
14. 校验输出文件存在
15. 使用 ffprobe 校验媒体属性
16. 收集截图、日志、输出文件和测试报告
17. 关闭应用
18. 输出本轮测试结论
```

## 5. 第一版核心测试范围

第一版只覆盖 P0 核心链路。

| 编号 | 优先级 | 用例 | 目标 |
|---|---|---|---|
| TC-P0-001 | P0 | 启动应用 | 验证应用能正常启动 |
| TC-P0-002 | P0 | 导入 MP4 视频 | 验证基础导入链路 |
| TC-P0-003 | P0 | MP4 转 MOV | 验证视频格式转换 |
| TC-P0-004 | P0 | MOV 转 MP4 | 验证视频格式转换 |
| TC-P0-005 | P0 | MP4 视频压缩 | 验证压缩功能 |
| TC-P0-006 | P0 | MP4 提取音频 | 验证音频提取功能 |
| TC-P0-007 | P0 | MP4 转 GIF | 验证视频转 GIF 功能 |

## 6. 测试数据设计

建议首版测试数据控制在小体积、短时长，保证回归执行速度和稳定性。

| 文件名 | 类型 | 建议时长 | 用途 |
|---|---|---|---|
| sample_with_audio.mp4 | MP4 | 3-10 秒 | 导入、转换、压缩、音频提取、转 GIF |
| sample_no_audio.mp4 | MP4 | 3-10 秒 | 后续验证无音频异常场景 |
| sample_mov.mov | MOV | 3-10 秒 | MOV 转 MP4 |
| invalid_file.txt | 非视频文件 | 不适用 | 后续验证非法导入 |

第一版 P0 只强制使用：

- `sample_with_audio.mp4`
- `sample_mov.mov`

测试数据要求：

- 文件内容固定，不随测试变化。
- 文件命名稳定。
- 文件体积尽量小。
- 源视频能被 `ffprobe` 正常解析。
- 源视频具备明确的音视频流信息。

## 7. 建议项目目录结构

```text
desktop-ui-auto/
  tests/
    test_smoke.py
    test_import.py
    test_video_convert.py
    test_video_compress.py
    test_audio_extract.py
    test_video_to_gif.py

  pages/
    main_window.py
    import_dialog.py
    export_dialog.py
    convert_panel.py
    compress_panel.py
    audio_panel.py
    gif_panel.py

  utils/
    app_runner.py
    video_probe.py
    file_assert.py
    screenshot.py
    logger.py
    wait.py
    paths.py

  test_data/
    sample_with_audio.mp4
    sample_no_audio.mp4
    sample_mov.mov
    invalid_file.txt

  outputs/
  reports/
  screenshots/
  logs/

  pytest.ini
  requirements.txt
  README.md
```

目录职责：

| 目录或文件 | 职责 |
|---|---|
| `tests/` | 存放测试用例 |
| `pages/` | 封装页面和控件操作 |
| `utils/` | 存放启动、等待、文件校验、视频校验等工具 |
| `test_data/` | 固定测试数据 |
| `outputs/` | 测试输出文件 |
| `reports/` | HTML 测试报告 |
| `screenshots/` | 失败截图 |
| `logs/` | 自动化日志和应用日志 |
| `pytest.ini` | pytest 配置和 marker |
| `requirements.txt` | Python 依赖 |
| `README.md` | 本地执行说明 |

## 8. 核心断言设计

### 8.1 启动应用

断言：

- 应用进程存在。
- 主窗口出现。
- 主窗口标题符合预期。
- 关键控件可见，例如导入按钮、功能入口。

失败时收集：

- 启动日志。
- 当前桌面截图。
- Appium page source。

### 8.2 导入 MP4

断言：

- 文件选择成功。
- UI 中展示导入文件名。
- 文件状态为可处理。
- 未出现错误提示。

失败时收集：

- 主窗口截图。
- 应用日志。
- 当前 UI 控件树。

### 8.3 MP4 转 MOV

断言：

- 输出文件存在。
- 输出文件大小大于 0。
- `ffprobe` 返回成功。
- 输出格式为 MOV 或 QuickTime 容器。
- 存在视频流。
- 如果源文件有音频，输出文件存在音频流。
- 输出时长与源文件接近。

建议允许误差：

```text
duration_diff <= 1 秒
```

### 8.4 MOV 转 MP4

断言：

- 输出文件存在。
- 输出文件大小大于 0。
- `ffprobe` 返回成功。
- 输出格式为 MP4。
- 存在视频流。
- 输出时长与源文件接近。

### 8.5 MP4 视频压缩

断言：

- 输出文件存在。
- 输出文件大小大于 0。
- 压缩后文件小于源文件。
- `ffprobe` 返回成功。
- 输出文件存在视频流。
- 输出时长与源文件接近。

压缩断言注意：

- 如果产品存在“极低压缩率”配置，可能导致输出文件不一定明显变小。
- 第一版应使用固定压缩参数，确保预期结果稳定。

### 8.6 MP4 提取音频

断言：

- 输出音频文件存在。
- 输出文件大小大于 0。
- `ffprobe` 返回成功。
- 输出文件存在音频流。
- 输出文件不存在视频流，或符合产品设计。
- 音频时长与源视频接近。

### 8.7 MP4 转 GIF

断言：

- 输出 `.gif` 文件存在。
- 输出文件大小大于 0。
- `ffprobe` 返回成功。
- 格式为 GIF。
- 存在视频流。
- 帧数大于 1，或通过帧率和时长判断为动画。
- 分辨率符合固定输出参数。
- 时长与产品配置接近。

GIF 不建议在第一版做主观画质断言，只做基础有效性和媒体属性校验。

## 9. ffprobe 校验规则

建议封装统一的 `video_probe.py`，返回结构化信息。

需要读取的信息：

```text
format_name
duration
size
streams
video_stream_count
audio_stream_count
width
height
avg_frame_rate
nb_frames
```

通用校验规则：

| 类型 | 校验 |
|---|---|
| 视频文件 | 存在 video stream |
| 音频文件 | 存在 audio stream |
| GIF 文件 | 格式为 gif，存在 video stream |
| 转换文件 | 格式符合预期，时长接近 |
| 压缩文件 | 文件变小，视频流存在 |
| 提取音频 | 音频流存在 |

## 10. pytest marker 设计

建议配置：

```ini
[pytest]
markers =
    smoke: 最小冒烟测试
    core: 核心回归测试
    convert: 视频格式转换
    compress: 视频压缩
    audio: 音频提取
    gif: 视频转 GIF
```

执行命令：

```bash
pytest tests/ -m smoke --html=reports/smoke.html
pytest tests/ -m core --html=reports/core_regression.html
pytest tests/test_video_to_gif.py -m gif --html=reports/gif.html
```

## 11. 一周详细执行计划

### Day 1：环境和可测试性确认

目标：

- 确认 macOS 环境能支持自动化执行。
- 确认 Qt `objectName` 能通过 accessibility 暴露。
- 准备固定测试数据。

任务：

- 安装 Python。
- 安装 `ffmpeg` 和 `ffprobe`。
- 安装 Appium。
- 安装 Appium mac2 driver。
- 开启 macOS accessibility 权限。
- 准备被测应用安装包。
- 准备测试视频。
- 手工执行 7 条 P0 链路，确认产品功能可用。
- 记录每个功能入口对应的 `objectName`。

验收：

- `ffprobe` 能解析测试视频。
- Appium 能连接 macOS。
- 自动化脚本能看到应用主窗口。
- 核心控件能通过稳定标识定位。

### Day 2：基础框架搭建

目标：

- 完成 pytest 工程骨架。
- 实现应用启动、关闭、截图、日志基础能力。

任务：

- 创建目录结构。
- 配置 `pytest.ini`。
- 编写 `app_runner.py`。
- 编写 `paths.py`。
- 编写 `logger.py`。
- 编写 `screenshot.py`。
- 编写第一条 smoke 用例。

验收：

- 执行 smoke 用例能启动应用。
- 主窗口出现后测试通过。
- 测试结束能关闭应用。
- 失败时能保存截图。

### Day 3：导入流程自动化

目标：

- 自动完成 MP4 文件导入。

任务：

- 编写 `main_window.py`。
- 编写 `import_dialog.py`。
- 封装点击导入按钮。
- 封装选择测试文件。
- 封装导入成功断言。
- 编写 `test_import.py`。

验收：

- 脚本能导入 `sample_with_audio.mp4`。
- UI 中能识别导入文件。
- 失败时能保存截图和 page source。

### Day 4：视频格式转换自动化

目标：

- 覆盖 MP4 转 MOV 和 MOV 转 MP4。

任务：

- 编写 `convert_panel.py`。
- 编写 `video_probe.py`。
- 封装选择输出格式。
- 封装设置输出目录。
- 封装点击开始转换。
- 封装等待任务完成。
- 编写 `test_video_convert.py`。

验收：

- MP4 转 MOV 通过。
- MOV 转 MP4 通过。
- 输出文件格式、时长、视频流校验通过。

### Day 5：视频压缩和音频提取自动化

目标：

- 覆盖 MP4 压缩和 MP4 提取音频。

任务：

- 编写 `compress_panel.py`。
- 编写 `audio_panel.py`。
- 封装压缩参数选择。
- 封装音频格式选择。
- 编写 `test_video_compress.py`。
- 编写 `test_audio_extract.py`。

验收：

- MP4 压缩通过。
- 压缩后文件小于源文件。
- MP4 提取音频通过。
- 输出音频文件存在音频流。

### Day 6：视频转 GIF 和报告整理

目标：

- 覆盖 MP4 转 GIF。
- 整理 smoke 和 core 回归测试集。

任务：

- 编写 `gif_panel.py`。
- 封装 GIF 参数选择。
- 编写 `test_video_to_gif.py`。
- 补齐 `pytest` marker。
- 生成 HTML 报告。
- 整理失败截图和日志目录。

验收：

- MP4 转 GIF 通过。
- GIF 文件格式正确。
- GIF 帧数或动画属性有效。
- `pytest -m core` 能执行 7 条 P0 用例。

### Day 7：稳定性优化和交付

目标：

- 降低误报。
- 整理交付文档。
- 完成第一版试跑。

任务：

- 替换硬编码 sleep 为显式等待。
- 清理测试前后的输出目录。
- 固定测试数据路径。
- 固定报告输出路径。
- 编写 README。
- 连续执行 3 轮核心回归。
- 记录不稳定点和已知限制。

验收：

- 3 轮核心回归结果稳定。
- 每次失败都有可追踪证据。
- README 能指导新人本地执行。
- 第一版可交付。

## 12. 执行命令建议

安装依赖：

```bash
pip install -r requirements.txt
```

启动 Appium：

```bash
appium
```

执行冒烟测试：

```bash
pytest tests/ -m smoke --html=reports/smoke.html
```

执行核心回归：

```bash
pytest tests/ -m core --html=reports/core_regression.html
```

执行单功能调试：

```bash
pytest tests/test_video_convert.py -v
pytest tests/test_video_compress.py -v
pytest tests/test_audio_extract.py -v
pytest tests/test_video_to_gif.py -v
```

## 13. 缺陷定位策略

当自动化用例失败时，按以下顺序判断：

1. 应用是否启动成功。
2. UI 控件是否能定位。
3. 文件是否正确导入。
4. 输出目录是否有文件生成。
5. 任务是否超时。
6. 应用日志是否有错误。
7. `ffprobe` 是否能解析输出文件。
8. 输出文件属性是否与预期一致。

失败分类：

| 类型 | 判断依据 |
|---|---|
| 产品缺陷 | 手工复现同样失败，日志或输出结果异常 |
| 脚本缺陷 | 手工正常，脚本定位或等待失败 |
| 环境问题 | 权限、路径、Appium、系统弹窗导致失败 |
| 测试数据问题 | 源文件损坏或不符合用例前置条件 |

## 14. 风险与应对

| 风险 | 影响 | 应对 |
|---|---|---|
| Qt `objectName` 未暴露到 macOS accessibility | UI 定位不稳定 | 让研发确认 accessibility 映射；必要时补充 accessibilityName |
| 文件选择器难以自动化 | 导入流程不稳定 | 优先使用原生控件定位；必要时用 pyautogui 兜底 |
| 不支持命令行参数 | 环境初始化麻烦 | 用脚本清理固定配置和输出目录 |
| 视频处理耗时不稳定 | 用例超时 | 使用短视频样本，等待任务完成状态和输出文件双重判断 |
| 压缩后文件不一定变小 | 压缩断言误报 | 固定压缩参数，选择能稳定变小的测试视频 |
| GIF 帧数读取不稳定 | GIF 校验误报 | 同时使用格式、视频流、时长、分辨率等多维校验 |
| 无 CI/CD | 无法自动触发 | 第一版本地一键执行，第二阶段接入 CI |

## 15. 第二阶段建议

第一版稳定后，再推进以下内容：

- 接入 CI/CD。
- 增加 Windows 平台自动化。
- 扩展 P1 异常场景：
  - 不支持格式导入。
  - 无音频视频提取。
  - 输出路径无权限。
  - 转换中取消。
  - 重复文件名导出。
- 增加更多格式矩阵：
  - MP4、MOV、AVI、MKV、WEBM。
  - MP3、WAV、AAC。
  - GIF 不同分辨率和帧率。
- 增加稳定性测试：
  - 连续处理多个文件。
  - 长视频处理。
  - 批量任务。
- 增加测试报告趋势统计。

## 16. 第一版交付清单

第一版完成时，应交付：

- 自动化测试工程。
- 7 条 P0 核心用例。
- 固定测试数据。
- 本地执行说明。
- HTML 测试报告。
- 失败截图目录。
- 自动化日志目录。
- 应用日志收集方式。
- 已知问题和限制说明。
- 第二阶段扩展建议。

## 17. 最终建议

第一版不要追求覆盖所有功能。当前最重要的是把核心功能自动化闭环跑通：

```text
启动应用
导入视频
视频格式转换
视频压缩
音频提取
视频转 GIF
ffprobe 校验结果
生成报告
```

只要这条链路稳定，就能在没有 CI/CD 的情况下先建立每日手动触发的核心回归机制。后续再逐步扩展 Windows、CI/CD、异常场景和更多格式矩阵。
