import textwrap
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from nonebot.log import logger
from math import cos, sin, pi
from .config import error_config, BotRunTimeError

def all_images_draw(error_msg:str,error_detail:str) -> Image.Image:
    card_width = 600  # 内部卡片宽度
    main_padding = 40  # 主卡片边距
    inner_padding = 15  # 内部元素边距
    card_padding = 15  # 卡片内部边距
    card_spacing = 20  # 卡片之间的间距
    title_height = 75  # 标题区域高度
    line_height = 25   # 行高定义
    main_width = int(card_width + main_padding * 2)  # 主卡片总宽度
    card_draw_width = int(card_width - card_padding * 2)  # 减小卡片实际宽度
    min_card_height = 100  # 最小卡片高度

    try:
        font_path = error_config.error_image_font
        title_font = ImageFont.truetype(font_path, 28)
        normal_font = ImageFont.truetype(font_path, 16)
    except (AttributeError, OSError):
        try:
            font_path = "C:/Windows/Fonts/msyh.ttc"
            title_font = ImageFont.truetype(font_path, 28)
            normal_font = ImageFont.truetype(font_path, 16)
        except OSError:
            try:
                title_font = ImageFont.load_default()
                normal_font = ImageFont.load_default()
                line_height = 20
            except:
                logger.error("无法加载任何字体")
                raise BotRunTimeError("字体加载失败")
    
    wrapper = textwrap.TextWrapper(width=60)
    error_lines = wrapper.wrap(error_msg)
    detail_lines = wrapper.wrap(error_detail)
    
    error_card_height = max(
        min_card_height,
        35 + len(error_lines) * line_height + card_padding * 3
    )
    detail_card_height = max(
        min_card_height,
        45 + len(detail_lines) * line_height + card_padding * 4
    )
    
    content_height = int(
        title_height +          # 标题高度
        inner_padding +     # 标题和第一个卡片之间的间距
        error_card_height +     # 错误卡片高度
        card_spacing * 2 +      # 卡片之间的间距
        detail_card_height +    # 详细追踪卡片高度
        inner_padding      # 底部额外间距
    )
    main_height = int(content_height + main_padding * 2)
    img = draw_main_card(main_width, main_height, title_font, main_padding)
    draw = ImageDraw.Draw(img, "RGBA")
    start_x = (main_width - card_draw_width) // 2
    current_y = title_height + inner_padding

    current_y = draw_error_card(
        draw, error_lines, normal_font,
        current_y, start_x,
        line_height, card_draw_width
    )
    
    draw_traceback_card(
        draw, detail_lines, normal_font,
        current_y + card_spacing,
        start_x,
        line_height, card_draw_width
    )

    draw_footer_info(
        draw=draw,
        font=normal_font,
        start_x=main_padding,
        height=main_height,
        width=main_width,
        bottom_padding=main_padding
    )
    bio = BytesIO()
    img.save(bio, format='PNG', quality=error_config.error_image_quality)
    return bio.getvalue()

def draw_main_card(width: int, total_height: int, font: ImageFont.FreeTypeFont, padding: int) -> Image.Image:
    """绘制主背景卡片"""
    # 基础颜色定义
    bg_color = (28, 28, 30)
    border_color = (100, 100, 110)
    accent_color = (255, 69, 58)
    
    img = Image.new("RGB", (width, total_height), bg_color)
    draw = ImageDraw.Draw(img)
    
    for i in range(50):
        opacity = int(25 * (1 - i/50))
        y_pos = i * 2
        draw.line([(0, y_pos), (width, y_pos)], fill=(255, 255, 255, opacity))
    
    border_width = 2
    draw.rounded_rectangle(
        [(padding//2, padding//2), 
         (width-padding//2, total_height-padding//2)],
        radius=15,
        outline=border_color,
        width=border_width
    )
    
    clock_size = 30
    clock_positions = [
        (padding, padding),
        (width-padding, padding),
        (width-padding, total_height-padding),
        (padding, total_height-padding)
    ]
    
    for i, (x, y) in enumerate(clock_positions):
        draw.ellipse(
            [x-clock_size//2, y-clock_size//2, 
             x+clock_size//2, y+clock_size//2],
            outline=border_color,
            width=2
        )
        
        center = (x, y)
        hour_angle = i * 90 + 45
        hour_length = clock_size//3
        hour_end = (
            x + hour_length * cos(hour_angle * pi/180),
            y + hour_length * sin(hour_angle * pi/180)
        )
        draw.line([center, hour_end], fill=accent_color, width=2)
        minute_angle = i * 90
        minute_length = clock_size//2.5
        minute_end = (
            x + minute_length * cos(minute_angle * pi/180),
            y + minute_length * sin(minute_angle * pi/180)
        )
        draw.line([center, minute_end], fill=accent_color, width=2)
        
        draw.ellipse([x-2, y-2, x+2, y+2], fill=accent_color)
    
    for i in range(len(clock_positions)):
        start = clock_positions[i]
        end = clock_positions[(i+1) % len(clock_positions)]
        
        dash_length = 10
        total_length = ((end[0]-start[0])**2 + (end[1]-start[1])**2)**0.5
        num_dashes = int(total_length / (dash_length * 2))
        
        for j in range(num_dashes):
            t1 = j / num_dashes
            t2 = (j + 0.5) / num_dashes
            dash_start = (
                start[0] + (end[0]-start[0])*t1,
                start[1] + (end[1]-start[1])*t1
            )
            dash_end = (
                start[0] + (end[0]-start[0])*t2,
                start[1] + (end[1]-start[1])*t2
            )
            draw.line([dash_start, dash_end], fill=border_color, width=1)
    
    title_text = "错误报告"
    title_width = draw.textlength(title_text, font=font)
    title_x = (width - title_width) // 2
    title_y = padding * 0.75
    
    title_padding = 20
    draw.rounded_rectangle(
        [title_x - title_padding, 
         title_y - 5,
         title_x + title_width + title_padding,
         title_y + 35],
        radius=8,
        fill=(38, 38, 40)
    )
    draw.text((title_x, title_y), title_text, font=font, fill=accent_color)
    return img

def draw_error_card(draw: ImageDraw, error_lines: list, font: ImageFont.FreeTypeFont, 
                   start_y: int, start_x: int, line_height: int, width: int) -> int:
    """绘制错误信息卡片"""
    current_y = start_y
    card_bg = (48, 48, 52)
    text_color = (242, 242, 247)
    title_color = (255, 159, 10)
    border_color = (120, 120, 128)
    
    padding = 20
    title_height = 30
    content_height = title_height + 2 * line_height + padding * 2  # 固定两行文本
    card_height = max(100, content_height)
    
    shadow_offset = 4
    for i in range(shadow_offset):
        draw.rounded_rectangle(
            [(start_x + i, current_y + i),
             (start_x + width - i, current_y + card_height - i)],
            radius=12,
            fill=(40, 40, 45)
        )
    
    draw.rounded_rectangle(
        [(start_x, current_y),
         (start_x + width, current_y + card_height)],
        radius=12,
        fill=card_bg
    )
    
    draw.rounded_rectangle(
        [(start_x, current_y),
         (start_x + width, current_y + card_height)],
        radius=12,
        outline=border_color,
        width=2
    )
    
    text_x = start_x + padding
    content_y = current_y + padding
    draw.text((text_x, content_y), "错误信息:", font=font, fill=title_color)
    content_y += line_height * 1.5
    
    text_start_x = text_x + 10
    if error_lines:
        error_text = "".join(error_lines)
        split_text = error_text.split("&hx&")
        for i, line in enumerate(split_text):
            if line.strip():
                draw.text((text_start_x, content_y), line.strip(), font=font, fill=text_color)
                content_y += line_height
                if i >= 1:
                    break
    return current_y + card_height + 10

def draw_traceback_card(draw: ImageDraw, detail_lines: list, font: ImageFont.FreeTypeFont,
                       start_y: int, start_x: int, line_height: int, 
                       width: int) -> None:
    """绘制详细追踪卡片"""
    current_y = start_y
    card_bg = (48, 48, 52)
    text_color = (242, 242, 247)
    title_color = (48, 209, 88)
    version_color = (142, 142, 147)
    border_color = (120, 120, 128)  # 添加边框颜色
    
    padding = 20
    content_height = 35 + len(detail_lines) * line_height + padding * 2
    card_height = max(120, content_height)
    
    shadow_offset = 4
    for i in range(shadow_offset):
        draw.rounded_rectangle(
            [(start_x + i, current_y + i),
             (start_x + width - i, current_y + card_height - i)],
            radius=12,
            fill=(40, 40, 45)
        )
    
    draw.rounded_rectangle(
        [(start_x, current_y),
         (start_x + width, current_y + card_height)],
        radius=12,
        fill=card_bg
    )
    
    draw.rounded_rectangle(
        [(start_x, current_y),
         (start_x + width, current_y + card_height)],
        radius=12,
        outline=border_color,
        width=2
    )

    text_x = start_x + padding
    content_y = current_y + padding
    draw.text((text_x, content_y), "详细追踪:", font=font, fill=title_color)
    content_y += line_height * 1.2
    
    text_start_x = text_x + 10
    for line in detail_lines:
        draw.text((text_start_x, content_y), line, font=font, fill=text_color)
        content_y += line_height

def draw_footer_info(draw: ImageDraw, font: ImageFont.FreeTypeFont,
                    start_x: int, height: int, width: int, 
                    bottom_padding: int) -> None:
    """绘制底部信息"""
    small_font = ImageFont.truetype(font.path, size=12)
    
    version_color = (255, 215, 0)
    version_label_color = (218, 165, 32)
    copyright_color = (218, 165, 32)
    
    line_spacing = 25
    version_y = int(height - bottom_padding * 2.40)
    copyright_y = version_y + line_spacing
    
    version_label = "Version: "
    version_number = f"{error_config.version}"

    label_width = draw.textlength(version_label, font=small_font)
    number_width = draw.textlength(version_number, font=small_font)
    total_version_width = label_width + number_width
    version_x = (width - total_version_width) // 2
    number_x = version_x + label_width

    draw.text(
        (version_x, version_y),
        version_label,
        font=small_font,
        fill=version_label_color
    )
    
    draw.text(
        (number_x, version_y),
        version_number,
        font=small_font,
        fill=version_color
    )
    
    copyright_text = "nonebot_plugin_error_report © 2025 huanxin996 github"
    copyright_width = draw.textlength(copyright_text, font=small_font)
    copyright_x = (width - copyright_width) // 2
    draw.text(
        (copyright_x, copyright_y),
        copyright_text,
        font=small_font,
        fill=copyright_color
    )