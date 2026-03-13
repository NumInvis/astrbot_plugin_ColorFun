# VisualFun - 视觉娱乐插件

🎨 移植自 nonebot-plugin-color 和 nonebot-plugin-simple-setu 的 AstrBot 插件，支持颜色图片生成和色图获取。

## ✨ 功能特性

- 🎨 **颜色生成** - 生成指定颜色的图片，支持多种颜色格式
- 🌈 **渐变色** - 支持多色渐变生成
- 🎨 **色图获取** - 获取随机色图
- 🦵 **腿子图** - 获取腿子图
- 📖 **颜色信息** - 显示HEX、RGB值

## 🚀 安装

### 方式一：通过 AstrBot 插件市场安装

1. 打开 AstrBot 管理面板
2. 进入「插件」→「插件市场」
3. 搜索 `VisualFun` 并安装

### 方式二：手动安装

1. 克隆仓库到插件目录：
   ```bash
   cd /path/to/astrbot/data/plugins
   git clone https://github.com/NumInvis/astrbot_plugin_VisualFun.git
   ```

2. 重启 AstrBot

## ⚙️ 配置

在 AstrBot 插件配置面板中设置：

| 配置项 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `admin_users` | 列表 | 管理员用户ID列表 | `[]` |

## 📖 使用指南

### 命令列表

#### 🎨 颜色命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/颜色 <颜色值>` | 生成颜色图片 | `/颜色 红` |

**支持的颜色格式：**
- 颜色名: `红`、`蓝`、`green`、`yellow`
- 十六进制: `#FF0000`、`FF0000`、`0xFF0000`
- RGB: `rgb(255,0,0)` 或 `255 0 0`
- 渐变色: `红;黄;蓝` 或 `#FF0000;#00FF00`

#### 📷 图片命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/色图 [标签]` | 获取随机色图 | `/色图 二次元` |
| `/腿子` | 获取腿子图 | `/腿子` |
| `/看看腿` | 快捷命令 | `/看看腿` |

### 使用示例

#### 1️⃣ 生成颜色图片
```
/颜色 红
```
生成红色图片，显示HEX和RGB值。

#### 2️⃣ 渐变色
```
/颜色 红;黄;蓝
```
生成红到黄到蓝的渐变色图片。

#### 3️⃣ 获取色图
```
/色图 二次元
```
获取标签为"二次元"的色图。

## 🎨 颜色格式详解

### 颜色名称
支持中文和英文颜色名：
- 中文: 红、黄、蓝、绿、黑、白、粉、紫、橙...
- 英文: red、yellow、blue、green、black、white...

### 十六进制
- `#FF0000` - 标准格式
- `FF0000` - 省略#号
- `0xFF0000` - 0x前缀
- `#F00` - 简写格式

### RGB格式
- `rgb(255, 0, 0)` - CSS格式
- `255 0 0` - 空格分隔

### 渐变色
使用分号 `;` 或 `；` 分隔多个颜色：
- `红;黄;蓝`
- `#FF0000;#00FF00;#0000FF`

## 🤝 致谢

本项目参考了以下开源项目：

- **参考项目**：[nonebot-plugin-color](https://github.com/lgc-NB2Dev/nonebot-plugin-color) - 颜色生成逻辑
- **参考项目**：[nonebot-plugin-simple-setu](https://github.com/nomdn/nonebot-plugin-simple-setu) - 色图获取功能
- **框架支持**：[AstrBot](https://github.com/Soulter/AstrBot) - 机器人框架

感谢以上项目的作者们！❤️

## 📄 License

MIT License

---

<p align="center">
  Made with ❤️ for visual fun
</p>
