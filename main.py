"""
ColorFun - 颜色生成插件
专注于颜色生成功能
版本: 1.0.0
功能: 强大的颜色生成与可视化工具
"""

import io
import re
import math
import random
from typing import Optional, List, Tuple, Dict, Any
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register
from astrbot.core.message.message_event_result import MessageChain
import astrbot.core.message.components as Comp


@register("astrbot_plugin_ColorFun", "NumInvis", "ColorFun - 强大的颜色生成与可视化工具", "1.0.0")
class ColorFunPlugin(Star):
    """ColorFun 颜色生成插件"""

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

    # 颜色主题
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
        self.context = context
        logger.info("ColorFun 插件已初始化")

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

        # 4. 检查HSL格式: hsl(120, 100%, 50%)
        hsl_pattern = r'^hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)$'
        match = re.match(hsl_pattern, color_input)
        if match:
            h, s, l = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if 0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100:
                # HSL转RGB
                h /= 360.0
                s /= 100.0
                l /= 100.0
                
                if s == 0:
                    r = g = b = l
                else:
                    def hue2rgb(p, q, t):
                        if t < 0: t += 1
                        if t > 1: t -= 1
                        if t < 1/6: return p + (q - p) * 6 * t
                        if t < 1/2: return q
                        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
                        return p
                    
                    q = l * (1 + s) if l < 0.5 else l + s - l * s
                    p = 2 * l - q
                    r = hue2rgb(p, q, h + 1/3)
                    g = hue2rgb(p, q, h)
                    b = hue2rgb(p, q, h - 1/3)
                
                r, g, b = int(r * 255), int(g * 255), int(b * 255)
                hex_val = f"#{r:02X}{g:02X}{b:02X}"
                return (hex_val, f"hsl({h*360:.0f}, {s*100:.0f}%, {l*100:.0f}%)")

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

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """将十六进制颜色转换为RGB"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join(c * 2 for c in hex_color)
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)

    def _rgb_to_hex(self, r: int, g: int, b: int) -> str:
        """将RGB转换为十六进制颜色"""
        return f"#{r:02X}{g:02X}{b:02X}"

    def _rgb_to_hsl(self, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """将RGB转换为HSL"""
        r, g, b = r/255.0, g/255.0, b/255.0
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        h, s, l = 0, 0, (max_val + min_val) / 2
        
        if max_val != min_val:
            d = max_val - min_val
            s = d / (1 - abs(2 * l - 1))
            if max_val == r:
                h = (g - b) / d + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / d + 2
            else:
                h = (r - g) / d + 4
            h /= 6
        
        return (h * 360, s * 100, l * 100)

    def _create_color_image(self, hex_color: str, width: int = 400, height: int = 400, style: str = "solid") -> Image.Image:
        """创建颜色图片，支持多种样式"""
        r, g, b = self._hex_to_rgb(hex_color)
        
        # 创建基础图片
        img = Image.new('RGB', (width, height), (r, g, b))
        draw = ImageDraw.Draw(img)
        
        # 应用不同样式
        if style == "gradient":
            # 对角线渐变
            for y in range(height):
                for x in range(width):
                    ratio = (x + y) / (width + height)
                    new_r = int(r * (1 - ratio) + 255 * ratio)
                    new_g = int(g * (1 - ratio) + 255 * ratio)
                    new_b = int(b * (1 - ratio) + 255 * ratio)
                    draw.point((x, y), fill=(new_r, new_g, new_b))
        elif style == "pattern":
            # 网格图案
            grid_size = 20
            for y in range(0, height, grid_size):
                for x in range(0, width, grid_size):
                    if (x // grid_size + y // grid_size) % 2 == 0:
                        draw.rectangle([x, y, x + grid_size, y + grid_size], fill=(r, g, b))
                    else:
                        draw.rectangle([x, y, x + grid_size, y + grid_size], fill=(255-r, 255-g, 255-b))
        elif style == "blur":
            # 模糊效果
            img = img.filter(ImageFilter.GaussianBlur(radius=10))
            draw = ImageDraw.Draw(img)
        elif style == "noise":
            # 噪点效果
            for y in range(height):
                for x in range(width):
                    noise = int(random.uniform(-30, 30))
                    new_r = max(0, min(255, r + noise))
                    new_g = max(0, min(255, g + noise))
                    new_b = max(0, min(255, b + noise))
                    draw.point((x, y), fill=(new_r, new_g, new_b))

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

    def _create_gradient_image(self, colors: List[Tuple[str, str]], width: int = 400, height: int = 400, direction: str = "vertical") -> Image.Image:
        """创建渐变色图片，支持多种方向"""
        img = Image.new('RGB', (width, height))

        # 解析所有颜色
        rgb_colors = []
        for hex_color, _ in colors:
            r, g, b = self._hex_to_rgb(hex_color)
            rgb_colors.append((r, g, b))

        # 绘制渐变
        if direction == "vertical":
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
        elif direction == "horizontal":
            for x in range(width):
                # 计算当前列的颜色
                ratio = x / (width - 1)
                color_index = ratio * (len(rgb_colors) - 1)
                index1 = int(color_index)
                index2 = min(index1 + 1, len(rgb_colors) - 1)
                local_ratio = color_index - index1

                r = int(rgb_colors[index1][0] * (1 - local_ratio) + rgb_colors[index2][0] * local_ratio)
                g = int(rgb_colors[index1][1] * (1 - local_ratio) + rgb_colors[index2][1] * local_ratio)
                b = int(rgb_colors[index1][2] * (1 - local_ratio) + rgb_colors[index2][2] * local_ratio)

                draw = ImageDraw.Draw(img)
                draw.line([(x, 0), (x, height)], fill=(r, g, b))
        elif direction == "diagonal":
            for y in range(height):
                for x in range(width):
                    ratio = (x + y) / (width + height)
                    color_index = ratio * (len(rgb_colors) - 1)
                    index1 = int(color_index)
                    index2 = min(index1 + 1, len(rgb_colors) - 1)
                    local_ratio = color_index - index1

                    r = int(rgb_colors[index1][0] * (1 - local_ratio) + rgb_colors[index2][0] * local_ratio)
                    g = int(rgb_colors[index1][1] * (1 - local_ratio) + rgb_colors[index2][1] * local_ratio)
                    b = int(rgb_colors[index1][2] * (1 - local_ratio) + rgb_colors[index2][2] * local_ratio)

                    draw = ImageDraw.Draw(img)
                    draw.point((x, y), fill=(r, g, b))

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

    def _create_palette_image(self, colors: List[Tuple[str, str]], width: int = 400, height: int = 200) -> Image.Image:
        """创建颜色调色板图片"""
        img = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        # 计算每个颜色块的宽度
        block_width = width // len(colors)

        # 绘制颜色块
        for i, (hex_color, display_name) in enumerate(colors):
            r, g, b = self._hex_to_rgb(hex_color)
            x1 = i * block_width
            x2 = (i + 1) * block_width
            draw.rectangle([x1, 0, x2, height - 40], fill=(r, g, b))

            # 添加颜色名称
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            except:
                font = ImageFont.load_default()

            # 根据背景亮度选择文字颜色
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            text_color = (0, 0, 0) if brightness > 128 else (255, 255, 255)

            draw.text((x1 + 5, height - 35), display_name[:10], fill=text_color, font=font)
            draw.text((x1 + 5, height - 20), hex_color, fill=text_color, font=font)

        return img

    # ========== 命令处理 ==========

    @filter.command("颜色")
    async def cmd_color(self, event: AstrMessageEvent, color_input: str = "", style: str = "solid"):
        """生成颜色图片"""
        if not color_input:
            yield event.plain_result(
                "🎨 颜色生成器\n"
                "用法: /颜色 <颜色值> [样式]\n\n"
                "支持格式:\n"
                "• 颜色名: 红、蓝、green、yellow\n"
                "• 十六进制: #FF0000、FF0000、0xFF0000\n"
                "• RGB: rgb(255,0,0) 或 255 0 0\n"
                "• HSL: hsl(120, 100%, 50%)\n"
                "• 渐变色: 红;黄;蓝 或 #FF0000;#00FF00\n"
                "• 主题: 彩虹、冷色调、暖色调、中性色、自然、科技感、复古、霓虹\n\n"
                "支持样式:\n"
                "• solid: 纯色\n"
                "• gradient: 渐变\n"
                "• pattern: 网格\n"
                "• blur: 模糊\n"
                "• noise: 噪点\n\n"
                "示例:\n"
                "/颜色 红\n"
                "/颜色 #FF0000 gradient\n"
                "/颜色 255 0 0 pattern\n"
                "/颜色 红;黄;蓝\n"
                "/颜色 彩虹"
            )
            return

        # 检查是否为主题
        if color_input in self.COLOR_THEMES:
            theme_colors = self.COLOR_THEMES[color_input]
            parsed_colors = [(color, color) for color in theme_colors]
            try:
                img = self._create_palette_image(parsed_colors)
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)

                chain = MessageChain()
                chain.append(Comp.Plain(f"🎨 颜色主题: {color_input}\n"))
                chain.append(Comp.Image.fromBytes(buffer.getvalue()))
                yield event.chain_result(chain)
            except Exception as e:
                logger.error(f"生成主题调色板失败: {e}")
                yield event.plain_result("❌ 生成主题调色板失败")
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
                    img = self._create_color_image(hex_color, style=style)
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    buffer.seek(0)

                    r, g, b = self._hex_to_rgb(hex_color)
                    h, s, l = self._rgb_to_hsl(r, g, b)

                    chain = MessageChain()
                    chain.append(Comp.Plain(f"🎨 颜色: {display_name}\n"))
                    chain.append(Comp.Plain(f"HEX: {hex_color}\n"))
                    chain.append(Comp.Plain(f"RGB: ({r}, {g}, {b})\n"))
                    chain.append(Comp.Plain(f"HSL: ({h:.0f}, {s:.0f}%, {l:.0f}%)\n"))
                    chain.append(Comp.Image.fromBytes(buffer.getvalue()))
                    yield event.chain_result(chain)
                except Exception as e:
                    logger.error(f"生成颜色图片失败: {e}")
                    yield event.plain_result("❌ 生成颜色图片失败")
            else:
                yield event.plain_result(
                    "❌ 无法解析颜色\n"
                    "支持格式: 颜色名、#RRGGBB、RGB(r,g,b)、r g b、HSL(h,s%,l%)"
                )

    @filter.command("渐变")
    async def cmd_gradient(self, event: AstrMessageEvent, gradient_input: str = "", direction: str = "vertical"):
        """生成渐变色图片"""
        if not gradient_input:
            yield event.plain_result(
                "🌈 渐变色生成器\n"
                "用法: /渐变 <颜色1>;<颜色2>;<颜色3> [方向]\n\n"
                "支持方向:\n"
                "• vertical: 垂直\n"
                "• horizontal: 水平\n"
                "• diagonal: 对角线\n\n"
                "示例:\n"
                "/渐变 红;黄;蓝\n"
                "/渐变 #FF0000;#00FF00;#0000FF horizontal\n"
                "/渐变 红;绿;蓝;紫 diagonal"
            )
            return

        gradient_colors = self._parse_gradient(gradient_input)
        if gradient_colors:
            try:
                img = self._create_gradient_image(gradient_colors, direction=direction)
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)

                chain = MessageChain()
                chain.append(Comp.Plain(f"🌈 渐变色: {' → '.join([c[1] for c in gradient_colors])}\n"))
                chain.append(Comp.Plain(f"方向: {direction}\n"))
                chain.append(Comp.Image.fromBytes(buffer.getvalue()))
                yield event.chain_result(chain)
            except Exception as e:
                logger.error(f"生成渐变色失败: {e}")
                yield event.plain_result("❌ 生成渐变色失败")
        else:
            yield event.plain_result("❌ 无法解析渐变色，请检查格式")

    @filter.command("调色板")
    async def cmd_palette(self, event: AstrMessageEvent, palette_input: str = ""):
        """生成颜色调色板"""
        if not palette_input:
            yield event.plain_result(
                "🎨 调色板生成器\n"
                "用法: /调色板 <颜色1>;<颜色2>;<颜色3>...\n"  
                "或: /调色板 <主题>\n\n"
                "支持主题:\n"
                "• 彩虹、冷色调、暖色调、中性色、自然、科技感、复古、霓虹\n\n"
                "示例:\n"
                "/调色板 红;黄;蓝;绿\n"
                "/调色板 #FF0000;#FFFF00;#0000FF\n"
                "/调色板 彩虹"
            )
            return

        # 检查是否为主题
        if palette_input in self.COLOR_THEMES:
            theme_colors = self.COLOR_THEMES[palette_input]
            parsed_colors = [(color, color) for color in theme_colors]
        else:
            # 解析颜色列表
            colors = re.split(r'[;；]', palette_input)
            colors = [c.strip() for c in colors if c.strip()]
            if len(colors) < 2:
                yield event.plain_result("❌ 请至少提供2种颜色")
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
            img = self._create_palette_image(parsed_colors)
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            chain = MessageChain()
            chain.append(Comp.Plain(f"🎨 调色板: {' → '.join([c[1] for c in parsed_colors])}\n"))
            chain.append(Comp.Image.fromBytes(buffer.getvalue()))
            yield event.chain_result(chain)
        except Exception as e:
            logger.error(f"生成调色板失败: {e}")
            yield event.plain_result("❌ 生成调色板失败")

    @filter.command("color")
    async def cmd_color_en(self, event: AstrMessageEvent, color_input: str = "", style: str = "solid"):
        """Generate color image (English)"""
        await self.cmd_color(event, color_input, style)

    @filter.command("colorfun帮助")
    async def cmd_help(self, event: AstrMessageEvent):
        """显示帮助信息"""
        msg = """🎨 ColorFun - 强大的颜色生成与可视化工具

🎨 颜色命令:
/颜色 <颜色值> [样式] - 生成颜色图片
  支持格式:
  • 颜色名: 红、蓝、green、yellow
  • 十六进制: #FF0000、FF0000、0xFF0000
  • RGB: rgb(255,0,0) 或 255 0 0
  • HSL: hsl(120, 100%, 50%)
  • 渐变色: 红;黄;蓝 或 #FF0000;#00FF00
  • 主题: 彩虹、冷色调、暖色调、中性色、自然、科技感、复古、霓虹
  支持样式:
  • solid: 纯色、gradient: 渐变、pattern: 网格、blur: 模糊、noise: 噪点

🌈 渐变命令:
/渐变 <颜色1>;<颜色2>;<颜色3> [方向] - 生成渐变色图片
  支持方向: vertical(垂直)、horizontal(水平)、diagonal(对角线)

🎨 调色板命令:
/调色板 <颜色1>;<颜色2>;<颜色3>... - 生成颜色调色板
/调色板 <主题> - 生成主题调色板

📖 示例:
/颜色 红
/颜色 #FF0000 gradient
/颜色 255 0 0 pattern
/颜色 红;黄;蓝
/颜色 彩虹
/渐变 红;绿;蓝 horizontal
/调色板 冷色调

💡 提示:
• 颜色支持中文和英文名称
• 渐变色和调色板使用分号分隔多个颜色
• HSL格式: hsl(色相, 饱和度%, 亮度%)
• 主题包含预设的颜色组合"""

        yield event.plain_result(msg)