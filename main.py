"""
VisualFun - 视觉娱乐插件
整合 nonebot-plugin-color 和 nonebot-plugin-simple-setu
版本: 1.0.0
功能: 颜色生成 + 色图获取
"""

import io
import re
import random
import asyncio
import aiohttp
from typing import Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register
from astrbot.core.message.message_event_result import MessageChain
import astrbot.core.message.components as Comp


@register("astrbot_plugin_VisualFun", "NumInvis", "VisualFun - 颜色生成与美图获取", "1.0.0")
class VisualFunPlugin(Star):
    """VisualFun 视觉娱乐插件"""

    # 颜色名称映射
    COLOR_NAMES = {
        # 中文颜色名
        "红": "#FF0000", "红色": "#FF0000",
        "黄": "#FFFF00", "黄色": "#FFFF00",
        "蓝": "#0000FF", "蓝色": "#0000FF",
        "绿": "#00FF00", "绿色": "#00FF00",
        "黑": "#000000", "黑色": "#000000",
        "白": "#FFFFFF", "白色": "#FFFFFF",
        "灰": "#808080", "灰色": "#808080",
        "粉": "#FFC0CB", "粉色": "#FFC0CB",
        "紫": "#800080", "紫色": "#800080",
        "橙": "#FFA500", "橙色": "#FFA500",
        "青": "#00FFFF", "青色": "#00FFFF",
        "棕": "#A52A2A", "棕色": "#A52A2A",
        "金": "#FFD700", "金色": "#FFD700",
        "银": "#C0C0C0", "银色": "#C0C0C0",
        "天蓝": "#87CEEB", "天蓝色": "#87CEEB",
        "草绿": "#7CFC00", "草绿色": "#7CFC00",
        "玫红": "#FF1493", "玫红色": "#FF1493",
        "天青": "#008080", "天青色": "#008080",
        "藏青": "#000080", "藏青色": "#000080",
        "咖啡": "#6F4E37", "咖啡色": "#6F4E37",
        "柠檬": "#FFF44F", "柠檬黄": "#FFF44F",
        "薄荷": "#98FF98", "薄荷绿": "#98FF98",
        "珊瑚": "#FF7F50", "珊瑚色": "#FF7F50",
        "薰衣草": "#E6E6FA", "薰衣草紫": "#E6E6FA",
        "巧克力": "#D2691E", "巧克力色": "#D2691E",
        "番茄": "#FF6347", "番茄红": "#FF6347",
        "天空": "#87CEEB", "天空蓝": "#87CEEB",
        "森林": "#228B22", "森林绿": "#228B22",
        "海洋": "#006994", "海洋蓝": "#006994",
        "日落": "#FD5E53", "日落橙": "#FD5E53",
        "樱花": "#FFB7C5", "樱花粉": "#FFB7C5",
        # 英文颜色名
        "red": "#FF0000",
        "yellow": "#FFFF00",
        "blue": "#0000FF",
        "green": "#00FF00",
        "black": "#000000",
        "white": "#FFFFFF",
        "gray": "#808080", "grey": "#808080",
        "pink": "#FFC0CB",
        "purple": "#800080",
        "orange": "#FFA500",
        "cyan": "#00FFFF",
        "brown": "#A52A2A",
        "gold": "#FFD700",
        "silver": "#C0C0C0",
        "skyblue": "#87CEEB",
        "lime": "#00FF00",
        "magenta": "#FF00FF",
        "violet": "#EE82EE",
        "indigo": "#4B0082",
        "turquoise": "#40E0D0",
        "coral": "#FF7F50",
        "salmon": "#FA8072",
        "khaki": "#F0E68C",
        "plum": "#DDA0DD",
        "orchid": "#DA70D6",
    }

    # 图片API列表
    IMAGE_APIS = {
        "setu": [
            "https://api.lolicon.app/setu/v2",
            "https://api.vvhan.com/api/girl",
        ],
        "leg": [
            "https://api.vvhan.com/api/leg",
        ],
        "girl": [
            "https://api.vvhan.com/api/girl",
        ],
        "anime": [
            "https://api.waifu.im/search",
        ],
    }

    def __init__(self, context: Context):
        super().__init__(context)
        self.context = context
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info("VisualFun 插件已初始化")

    async def _get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self.session

    def _parse_color(self, color_input: str) -> Optional[Tuple[str, str]]:
        """
        解析颜色输入
        返回: (hex_color, display_name) 或 None
        """
        color_input = color_input.strip().lower()

        # 1. 检查颜色名称
        if color_input in self.COLOR_NAMES:
            hex_color = self.COLOR_NAMES[color_input]
            return (hex_color, color_input)

        # 2. 检查十六进制格式
        # 支持: #RGB, #RGBA, #RRGGBB, #RRGGBBAA, 0xRGB, RGB
        hex_patterns = [
            r'^#?([0-9a-fA-F]{3})$',      # RGB
            r'^#?([0-9a-fA-F]{4})$',      # RGBA
            r'^#?([0-9a-fA-F]{6})$',      # RRGGBB
            r'^#?([0-9a-fA-F]{8})$',      # RRGGBBAA
            r'^0x([0-9a-fA-F]{3,8})$',    # 0x格式
        ]

        for pattern in hex_patterns:
            match = re.match(pattern, color_input)
            if match:
                hex_val = match.group(1)
                # 转换为标准6位十六进制
                if len(hex_val) == 3:  # RGB -> RRGGBB
                    hex_val = ''.join(c * 2 for c in hex_val)
                elif len(hex_val) == 4:  # RGBA -> RRGGBB (忽略Alpha)
                    hex_val = ''.join(c * 2 for c in hex_val[:3])
                elif len(hex_val) == 8:  # RRGGBBAA -> RRGGBB
                    hex_val = hex_val[:6]

                return (f"#{hex_val.upper()}", f"#{hex_val.upper()}")

        # 3. 检查RGB格式: rgb(255, 255, 0) 或 255 255 0
        rgb_pattern1 = r'^rgb\((\d+),\s*(\d+),\s*(\d+)\)$'
        rgb_pattern2 = r'^(\d+)\s+(\d+)\s+(\d+)$'

        for pattern in [rgb_pattern1, rgb_pattern2]:
            match = re.match(pattern, color_input)
            if match:
                r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
                if all(0 <= x <= 255 for x in [r, g, b]):
                    hex_val = f"#{r:02X}{g:02X}{b:02X}"
                    return (hex_val, hex_val)

        return None

    def _parse_gradient(self, gradient_input: str) -> Optional[List[Tuple[str, str]]]:
        """
        解析渐变色输入
        支持: color1;color2;color3 或 color1；color2；color3
        """
        # 分割颜色
        colors = re.split(r'[;；]', gradient_input)
        colors = [c.strip() for c in colors if c.strip()]

        if len(colors) < 2:
            return None

        parsed_colors = []
        for color in colors:
            result = self._parse_color(color)
            if result:
                parsed_colors.append(result)
            else:
                return None

        return parsed_colors if len(parsed_colors) >= 2 else None

    def _create_color_image(self, hex_color: str, width: int = 400, height: int = 400) -> Image.Image:
        """创建纯色图片"""
        # 解析颜色
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)

        # 创建图片
        img = Image.new('RGB', (width, height), (r, g, b))
        draw = ImageDraw.Draw(img)

        # 添加文字
        text = hex_color
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()

        # 计算文字位置（居中）
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # 根据背景亮度选择文字颜色
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        text_color = (0, 0, 0) if brightness > 128 else (255, 255, 255)

        draw.text((x, y), text, fill=text_color, font=font)

        return img

    def _create_gradient_image(self, colors: List[Tuple[str, str]], width: int = 400, height: int = 400) -> Image.Image:
        """创建渐变色图片"""
        img = Image.new('RGB', (width, height))

        # 解析所有颜色
        rgb_colors = []
        for hex_color, _ in colors:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            rgb_colors.append((r, g, b))

        # 绘制渐变
        for y in range(height):
            # 计算当前行的颜色
            ratio = y / (height - 1)
            color_index = ratio * (len(rgb_colors) - 1)
            index1 = int(color_index)
            index2 = min(index1 + 1, len(rgb_colors) - 1)
            local_ratio = color_index - index1

            r = int(rgb_colors[index1][0] * (1 - local_ratio) + rgb_colors[index2][0] * local_ratio)
            g = int(rgb_colors[index1][1] * (1 - local_ratio) + rgb_colors[index2][1] * local_ratio)
            b = int(rgb_colors[index1][2] * (1 - local_ratio) + rgb_colors[index2][2] * local_ratio)

            draw = ImageDraw.Draw(img)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # 添加文字
        text = " → ".join([c[1] for c in colors])
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except:
            font = ImageFont.load_default()

        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = height - text_height - 20

        # 添加半透明背景
        overlay = Image.new('RGBA', (text_width + 20, text_height + 10), (0, 0, 0, 128))
        img = img.convert('RGBA')
        img.paste(overlay, (x - 10, y - 5), overlay)

        draw = ImageDraw.Draw(img)
        draw.text((x, y), text, fill=(255, 255, 255), font=font)

        return img.convert('RGB')

    async def _fetch_image(self, api_url: str) -> Optional[bytes]:
        """从API获取图片"""
        try:
            session = await self._get_session()
            async with session.get(api_url) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    if 'image' in content_type:
                        return await response.read()
                    else:
                        # 可能是JSON响应
                        data = await response.json()
                        # 尝试从JSON中提取图片URL
                        if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                            img_url = data['data'][0].get('url')
                            if img_url:
                                async with session.get(img_url) as img_response:
                                    if img_response.status == 200:
                                        return await img_response.read()
        except Exception as e:
            logger.error(f"获取图片失败: {e}")
        return None

    # ========== 命令处理 ==========

    @filter.command("色图")
    async def cmd_setu(self, event: AstrMessageEvent, tag: str = ""):
        """获取色图"""
        yield event.plain_result("🎨 正在获取色图，请稍候...")

        # 随机选择一个API
        api_url = random.choice(self.IMAGE_APIS["setu"])

        # 如果有tag，添加到URL
        if tag:
            api_url += f"?tag={tag}"

        image_data = await self._fetch_image(api_url)

        if image_data:
            chain = MessageChain()
            chain.append(Comp.Plain(f"🎨 色图来啦~\n"))
            if tag:
                chain.append(Comp.Plain(f"标签: {tag}\n"))
            chain.append(Comp.Image.fromBytes(image_data))
            yield event.chain_result(chain)
        else:
            yield event.plain_result("❌ 获取色图失败，请稍后再试")

    @filter.command("腿子")
    async def cmd_leg(self, event: AstrMessageEvent):
        """获取腿子图"""
        yield event.plain_result("🦵 正在获取腿子图，请稍候...")

        api_url = random.choice(self.IMAGE_APIS["leg"])
        image_data = await self._fetch_image(api_url)

        if image_data:
            chain = MessageChain()
            chain.append(Comp.Plain("🦵 腿子图来啦~\n"))
            chain.append(Comp.Image.fromBytes(image_data))
            yield event.chain_result(chain)
        else:
            yield event.plain_result("❌ 获取腿子图失败，请稍后再试")

    @filter.command("颜色")
    async def cmd_color(self, event: AstrMessageEvent, color_input: str = ""):
        """生成颜色图片"""
        if not color_input:
            yield event.plain_result(
                "🎨 颜色生成器\n"
                "用法: /颜色 <颜色值>\n\n"
                "支持格式:\n"
                "• 颜色名: 红、蓝、green、yellow\n"
                "• 十六进制: #FF0000、FF0000、0xFF0000\n"
                "• RGB: rgb(255,0,0) 或 255 0 0\n"
                "• 渐变色: 红;黄;蓝 或 #FF0000;#00FF00\n\n"
                "示例:\n"
                "/颜色 红\n"
                "/颜色 #FF0000\n"
                "/颜色 255 0 0\n"
                "/颜色 红;黄;蓝"
            )
            return

        # 检查是否为渐变色
        if ';' in color_input or '；' in color_input:
            gradient_colors = self._parse_gradient(color_input)
            if gradient_colors:
                try:
                    img = self._create_gradient_image(gradient_colors)
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    buffer.seek(0)

                    chain = MessageChain()
                    chain.append(Comp.Plain(f"🌈 渐变色: {' → '.join([c[1] for c in gradient_colors])}\n"))
                    chain.append(Comp.Image.fromBytes(buffer.getvalue()))
                    yield event.chain_result(chain)
                except Exception as e:
                    logger.error(f"生成渐变色失败: {e}")
                    yield event.plain_result("❌ 生成渐变色失败")
            else:
                yield event.plain_result("❌ 无法解析渐变色，请检查格式")
        else:
            # 单色
            color_result = self._parse_color(color_input)
            if color_result:
                hex_color, display_name = color_result
                try:
                    img = self._create_color_image(hex_color)
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    buffer.seek(0)

                    chain = MessageChain()
                    chain.append(Comp.Plain(f"🎨 颜色: {display_name}\n"))
                    chain.append(Comp.Plain(f"HEX: {hex_color}\n"))
                    r = int(hex_color[1:3], 16)
                    g = int(hex_color[3:5], 16)
                    b = int(hex_color[5:7], 16)
                    chain.append(Comp.Plain(f"RGB: ({r}, {g}, {b})\n"))
                    chain.append(Comp.Image.fromBytes(buffer.getvalue()))
                    yield event.chain_result(chain)
                except Exception as e:
                    logger.error(f"生成颜色图片失败: {e}")
                    yield event.plain_result("❌ 生成颜色图片失败")
            else:
                yield event.plain_result(
                    "❌ 无法解析颜色\n"
                    "支持格式: 颜色名、#RRGGBB、RGB(r,g,b)、r g b"
                )

    @filter.command("看看腿")
    async def cmd_look_leg(self, event: AstrMessageEvent):
        """看看腿（快捷命令）"""
        async for result in self.cmd_leg(event):
            yield result

    @filter.command("visual帮助")
    async def cmd_help(self, event: AstrMessageEvent):
        """显示帮助信息"""
        msg = """🎨 VisualFun - 视觉娱乐插件

📷 图片命令:
/色图 [标签] - 获取随机色图
/腿子 - 获取腿子图
/看看腿 - 快捷命令

🎨 颜色命令:
/颜色 <颜色值> - 生成颜色图片
  支持格式:
  • 颜色名: 红、蓝、green、yellow
  • 十六进制: #FF0000、FF0000
  • RGB: rgb(255,0,0) 或 255 0 0
  • 渐变色: 红;黄;蓝

📖 示例:
/颜色 红
/颜色 #FF0000
/颜色 255 0 0
/颜色 红;黄;蓝
/色图 二次元
/腿子

💡 提示:
• 颜色支持中文和英文名称
• 渐变色使用分号分隔
• 色图可以添加标签筛选"""

        yield event.plain_result(msg)
