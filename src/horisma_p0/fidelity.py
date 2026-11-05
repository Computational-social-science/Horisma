"""Image-derived OCR comparison; agreement is not qualified image fidelity."""
import re
from difflib import SequenceMatcher
from pathlib import Path
from .operators import digest


def locate_text_block(pdf_path, page_index, anchor):
    """Locate one complete extraction block; ambiguous anchors cannot select a region."""
    import pymupdf
    with pymupdf.open(pdf_path) as doc:
        if type(page_index) is not int or not 0 <= page_index < len(doc) or not isinstance(anchor, str) or not anchor.strip():
            raise ValueError('INVALID_PAGE_OR_ANCHOR')
        if doc[page_index].rotation:
            raise ValueError('ROTATED_PAGE_REQUIRES_COORDINATE_NORMALIZATION')
        matches = [b for b in doc[page_index].get_text('blocks') if anchor in b[4]]
        if len(matches) != 1:
            raise ValueError('UNIQUE_BLOCK_REQUIRED')
        b = matches[0]
        page = doc[page_index].rect
        return [max(0, b[0]-2), max(0, b[1]-2), min(page.width, b[2]+2), min(page.height, b[3]+2)]


def compare_text(reference, image_text):
    normalize = lambda s: re.sub(r'\s+', ' ', s).strip()
    a, b = normalize(reference), normalize(image_text)
    return {'agreement': SequenceMatcher(None, a, b).ratio(),
            'numbers_match': re.findall(r'\d+', a) == re.findall(r'\d+', b),
            'status': 'AGREEMENT_UNQUALIFIED' if a and a == b else 'UNRESOLVED',
            'fidelity_accepted': False}


def ocr_region(pdf_path, page_index, rect, model_dir):
    """Rasterize an explicit PDF-point region; only pre-existing local models."""
    import pymupdf
    from rapidocr import RapidOCR
    import numpy as np
    names = {'Det': 'PP-OCRv6_det_small.onnx',
             'Rec': 'PP-OCRv6_rec_small.onnx',
             'Cls': 'ch_ppocr_mobile_v2.0_cls_mobile.onnx'}
    models = {key: Path(model_dir) / name for key, name in names.items()}
    if not all(path.is_file() for path in models.values()):
        raise ValueError('LOCAL_OCR_WEIGHTS_REQUIRED')
    with pymupdf.open(pdf_path) as doc:
        if type(page_index) is not int or not 0 <= page_index < len(doc):
            raise ValueError('INVALID_PAGE')
        page = doc[page_index]
        if page.rotation:
            raise ValueError('ROTATED_PAGE_REQUIRES_COORDINATE_NORMALIZATION')
        clip = pymupdf.Rect(rect)
        if clip.is_empty or not page.rect.contains(clip):
            raise ValueError('INVALID_REGION')
        if clip.width * 2 > 10000 or clip.height * 2 > 10000 or clip.width * clip.height * 4 > 10000000:
            raise ValueError('RASTER_PIXEL_BUDGET_EXCEEDED')
        engine = RapidOCR(params={f'{key}.model_path': str(path) for key, path in models.items()})
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), clip=clip, alpha=False)
        pixels = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        result = engine(pixels)
        image_text = ' '.join(result.txts or [])
        extracted = page.get_text(clip=clip)
    return {'source_sha256': digest(Path(pdf_path).read_bytes()),
            'page_index': page_index, 'region_pdf_points': list(rect),
            'render_sha256': digest(pix.tobytes('png')), 'image_text': image_text,
            'extracted_text': extracted, 'comparison': compare_text(extracted, image_text),
            'model_sha256': {k: digest(v.read_bytes()) for k, v in models.items()},
            'engine': 'RapidOCR local ONNX; PyMuPDF rasterization',
            'qualified_for_acceptance': False}


def support_guard(model_supported, fidelity_status):
    """Unresolved OCR cannot be rescued by semantic model agreement."""
    return model_supported is True and fidelity_status == 'QUALIFIED_IMAGE_MATCH'
