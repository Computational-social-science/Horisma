"""Image fixtures and exact stop/go checks shared by local transcription backends."""
import io

from PIL import Image, ImageDraw


def render_control(case, config, font):
    image = Image.new('RGB', (config['image_width'], config['image_height']), 'white')
    draw = ImageDraw.Draw(image)
    box = draw.textbbox((20, 35), case['text'], font=font)
    if box[2] > image.width - 20 or box[3] > image.height - 10:
        raise ValueError('CONTROL_TEXT_CLIPPED')
    draw.text((20, 35), case['text'], font=font, fill='black')
    stream = io.BytesIO()
    image.save(stream, format='PNG')
    return stream.getvalue()


def screen_passed(rows, expected_count):
    return (expected_count > 0 and len(rows) == expected_count
            and all(row.get('literal_match') is True for row in rows))
