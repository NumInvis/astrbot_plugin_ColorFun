import io
import re
import random
from typing import Optional, List, Tuple
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register
from astrbot.core.message.components import Image, Plain


@register("astrbot_plugin_ColorFun", "NumInvis", "ColorFun - 强大的颜色生成与可视化工具", "1.0.0")
class ColorFunPlugin(Star):
    COLOR_NAMES = {
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
    }

    COLOR_THEMES = {
        "彩虹": ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#8B00FF"],
        "冷色调": ["#0000FF", "#00FFFF", "#008080", "#87CEEB", "#40E0D0"],
        "暖色调": ["#FF0000", "#FFA500", "#FFFF00", "#FF6347", "#D2691E"],
        "中性色": ["#000000", "#808080", "#C0C0C0", "#FFFFFF", "#A52A2A"],
        "自然": ["#228B22", "#7CFC00", "#98FF98", "#6F4E37", "#D2B48C"],
        "科技感": ["#00FFFF", "#0066CC", "#3399FF", "#99CCFF", "#000033"],
        "复古": ["#8B4513", "#A0522D", "#CD853F", "#DEB887", "#F5DEB3"],
        "霓虹": ["#FF00FF", "#00FFFF", "#FFFF00", "#FF0000", "#00FF00"],
    }

    def __init__(self, context: Context):
        super().__init__(context)
        logger.info("ColorFun 插件已初始化")

    def _parse_color(self, color_input: str) -> Optional[Tuple[str, str]]:
        color_input = color_input.strip().lower()

        if color_input in self.COLOR_NAMES:
            return (self.COLOR_NAMES[color_input], color_input)

        hex_patterns = [
            r'^#?([0-9a-fA-F]{3})$',
            r'^#?([0-9a-fA-F]{6})$',
        ]

        for pattern in hex_patterns:
            match = re.match(pattern, color_input)
            if match:
                hex_val = match.group(1)
                if len(hex_val) == 3:
                    hex_val = ''.join(c * 2 for c in hex_val)
                return (f"#{hex_val.upper()}", f"#{hex_val.upper()}")

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

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join(c * 2 for c in hex_color)
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)

    def _create_color_image(self, hex_color: str):
        r, g, b = self._hex_to_rgb(hex_color)
        img = PILImage.new('RGB', (800, 800), (r, g, b))
        return img

    def _create_gradient_image(self, colors: List[Tuple[str, str]]):
        img = PILImage.new('RGB', (800, 800))
        rgb_colors = []
        for hex_color, _ in colors:
            rgb_colors.append(self._hex_to_rgb(hex_color))

        for y in range(800):
            ratio = y / 799
            color_index = ratio * (len(rgb_colors) - 1)
            index1 = int(color_index)
            index2 = min(index1 + 1, len(rgb_colors) - 1)
            local_ratio = color_index - index1

            r = int(rgb_colors[index1][0] * (1 - local_ratio) + rgb_colors[index2][0] * local_ratio)
            g = int(rgb_colors[index1][1] * (1 - local_ratio) + rgb_colors[index2][1] * local_ratio)
            b = int(rgb_colors[index1][2] * (1 - local_ratio) + rgb_colors[index2][2] * local_ratio)

            draw = ImageDraw.Draw(img)
            draw.line([(0, y), (800, y)], fill=(r, g, b))

        return img

    def _create_palette_image(self, colors: List[Tuple[str, str]]):
        img = PILImage.new('RGB', (800, 400), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        block_width = 800 // len(colors)

        for i, (hex_color, _) in enumerate(colors):
            r, g, b = self._hex_to_rgb(hex_color)
            x1 = i * block_width
            x2 = (i + 1) * block_width
            draw.rectangle([x1, 0, x2, 400], fill=(r, g, b))

        return img

    @filter.command("颜色")
    async def cmd_color(self, event: AstrMessageEvent, color_input: str = ""):
        if not color_input:
            yield event.plain_result(
                "🎨 颜色生成器\n"
                "用法: /颜色 <颜色值>\n\n"
                "支持格式:\n"
                "• 颜色名: 红、蓝、green、yellow\n"
                "• 十六进制: #FF0000、FF0000\n"
                "• RGB: rgb(255,0,0) 或 255 0 0\n"
                "• 渐变色: 红;黄;蓝\n"
                "• 主题: 彩虹、冷色调、暖色调\n\n"
                "示例:\n"
                "/颜色 红\n"
                "/颜色 #FF0000\n"
                "/颜色 255 0 0\n"
                "/颜色 红;黄;蓝"
            )
            return

        if color_input in self.COLOR_THEMES:
            theme_colors = self.COLOR_THEMES[color_input]
            parsed_colors = [(color, color) for color in theme_colors]
            try:
                img = self._create_palette_image(parsed_colors)
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                yield event.chain_result([Plain(f"🎨 颜色主题: {color_input}\n"), Image.fromBytes(buffer.getvalue())])
            except Exception as e:
                logger.error(f"生成主题调色板失败: {e}")
                yield event.plain_result("❌ 生成主题调色板失败")
            return

        if ';' in color_input or '；' in color_input:
            colors = re.split(r'[;；]', color_input)
            colors = [c.strip() for c in colors if c.strip()]
            
            if len(colors) < 2:
                yield event.plain_result("❌ 渐变色需要至少2种颜色")
                return
            
            parsed_colors = []
            for color in colors:
                result = self._parse_color(color)
                if result:
                    parsed_colors.append(result)
                else:
                    yield event.plain_result(f"❌ 无法解析颜色: {color}")
                    return
            
            try:
                img = self._create_gradient_image(parsed_colors)
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                yield event.chain_result([Plain(f"🌈 渐变色: {' → '.join([c[1] for c in parsed_colors])}\n"), Image.fromBytes(buffer.getvalue())])
            except Exception as e:
                logger.error(f"生成渐变色失败: {e}")
                yield event.plain_result("❌ 生成渐变色失败")
            return

        color_result = self._parse_color(color_input)
        if color_result:
            hex_color, display_name = color_result
            try:
                img = self._create_color_image(hex_color)
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                yield event.chain_result([Plain(f"🎨 颜色: {display_name}\n"), Image.fromBytes(buffer.getvalue())])
            except Exception as e:
                logger.error(f"生成颜色图片失败: {e}")
                yield event.plain_result("❌ 生成颜色图片失败")
        else:
            yield event.plain_result(
                "❌ 无法解析颜色\n"
                "支持格式: 颜色名、#RRGGBB、RGB(r,g,b)、r g b"
            )

    @filter.command("色图")
    async def cmd_random_color_image(self, event: AstrMessageEvent):
        try:
            mode = random.choice(["gradient", "palette", "special", "single"])
            
            if mode == "gradient":
                num_colors = random.randint(2, 5)
                random_colors = []
                for _ in range(num_colors):
                    r = random.randint(0, 255)
                    g = random.randint(0, 255)
                    b = random.randint(0, 255)
                    hex_color = f"#{r:02X}{g:02X}{b:02X}"
                    random_colors.append((hex_color, hex_color))
                
                img = self._create_gradient_image(random_colors)
                description = f"🌈 随机渐变色 ({num_colors}色)\n颜色: {' → '.join([c[0] for c in random_colors])}"
            
            elif mode == "palette":
                num_colors = random.randint(4, 8)
                random_colors = []
                for _ in range(num_colors):
                    r = random.randint(0, 255)
                    g = random.randint(0, 255)
                    b = random.randint(0, 255)
                    hex_color = f"#{r:02X}{g:02X}{b:02X}"
                    random_colors.append((hex_color, hex_color))
                
                img = self._create_palette_image(random_colors)
                description = f"🎨 随机调色板 ({num_colors}色)\n颜色: {' → '.join([c[0] for c in random_colors])}"
            
            elif mode == "special":
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                hex_color = f"#{r:02X}{g:02X}{b:02X}"
                
                img = self._create_color_image(hex_color)
                description = f"🎭 随机色图\n颜色: {hex_color}\nRGB: ({r}, {g}, {b})"
            
            else:
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                hex_color = f"#{r:02X}{g:02X}{b:02X}"
                
                img = self._create_color_image(hex_color)
                description = f"🎨 随机纯色\n颜色: {hex_color}\nRGB: ({r}, {g}, {b})"

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            yield event.chain_result([Plain(f"🎨 随机色图生成成功！\n{description}\n"), Image.fromBytes(buffer.getvalue())])
            
        except Exception as e:
            logger.error(f"生成随机色图失败: {e}")
            yield event.plain_result("❌ 生成随机色图失败，请稍后再试")

    @filter.command("colorfun帮助")
    async def cmd_help(self, event: AstrMessageEvent):
        msg = """🎨 ColorFun - 强大的颜色生成与可视化工具

🎨 颜色命令:
/颜色 <颜色值> - 生成颜色图片
  支持格式:
  • 颜色名: 红、蓝、green、yellow
  • 十六进制: #FF0000、FF0000
  • RGB: rgb(255,0,0) 或 255 0 0
  • 渐变色: 红;黄;蓝
  • 主题: 彩虹、冷色调、暖色调

🎨 随机色图命令:
/色图 - 随机生成一张色图，包含完全随机的渐变和各种功能

📖 示例:
/颜色 红
/颜色 #FF0000
/颜色 255 0 0
/颜色 红;黄;蓝
/颜色 彩虹
/色图

💡 提示:
• 颜色支持中文和英文名称
• 渐变色使用分号分隔多个颜色
• 主题包含预设的颜色组合"""

        yield event.plain_result(msg)
