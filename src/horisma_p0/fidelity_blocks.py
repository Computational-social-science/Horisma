"""Loss-aware producer adapters; raw structures remain the primary retained output."""
import math


def inline_content(node, depth=0):
    if depth > 40:
        raise ValueError('STRUCTURE_DEPTH_BUDGET')
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return ''.join(inline_content(item, depth + 1) for item in node)
    if isinstance(node, dict):
        if 'content' in node:
            return inline_content(node['content'], depth + 1)
        return ''.join(inline_content(node[key], depth + 1) for key in ('children', 'blocks', 'items') if key in node)
    return ''


def normalize_blocks(backend, raw, kind):
    blocks = []
    if backend == 'docling':
        for item in raw.get('texts', []):
            for prov in item.get('prov', []):
                page = raw['pages'][str(prov['page_no'])]
                text=item.get('text','');span=prov.get('charspan',[0,len(text)])
                if (len(span)!=2 or any(type(value) is not int for value in span)
                        or not 0<=span[0]<=span[1]<=len(text)):
                    blocks.append({'text':text,'label':item.get('label'),'bbox':None,'item_ref':item['self_ref'],
                                   'coordinate_system':'UNPLACED_INVALID_CHARSPAN','geometry_error':'CHARSPAN_OUTSIDE_TEXT'})
                    break
                text=text[span[0]:span[1]]
                blocks.append({'text': text, 'label': item.get('label'), 'bbox': prov.get('bbox'),
                               'page_size': page['size'], 'coordinate_system': 'DOCLING_PDF_POINTS_WITH_DECLARED_ORIGIN',
                               'item_ref': item['self_ref']})
    elif backend == 'paddleocr':
        payload = raw['res']
        if kind == 'page':
            for item in payload.get('parsing_res_list', []):
                blocks.append({'text': item['block_content'], 'label': item['block_label'],
                               'bbox': item['block_bbox'], 'coordinate_system': 'INPUT_IMAGE_PIXELS_TOP_LEFT'})
        else:
            if len(payload['rec_texts']) != len(payload['rec_polys']):
                raise ValueError('OCR_TEXT_GEOMETRY_COUNT_MISMATCH')
            for text, polygon in zip(payload['rec_texts'], payload['rec_polys']):
                blocks.append({'text': text, 'label': 'text', 'polygon': polygon,
                               'coordinate_system': 'INPUT_IMAGE_PIXELS_TOP_LEFT'})
    elif backend == 'mineru':
        def visit(block, depth=0):
            if depth > 40:
                raise ValueError('STRUCTURE_DEPTH_BUDGET')
            content=block.get('content')
            if block.get('type') in {'list','index','image','table','chart','code'} and isinstance(content,list):
                for child in content:
                    if not isinstance(child,dict):raise ValueError('NESTED_BLOCK_REQUIRED')
                    visit(child,depth+1)
            elif 'content' in block:
                text = inline_content(block['content'])
                if text:
                    blocks.append({'text': text, 'label': block['type'], 'bbox': block.get('bbox'),
                                   'coordinate_system': 'NORMALIZED_TOP_LEFT', 'item_index': block.get('index')})
            for key in ('children', 'blocks', 'items'):
                for child in block.get(key, []):
                    if isinstance(child, dict):
                        visit(child, depth + 1)
        for page in raw['pages']:
            for block in page['blocks']:
                visit(block)
    else:
        raise ValueError('UNSUPPORTED_BACKEND')
    if any(not isinstance(block['text'], str) for block in blocks):
        raise ValueError('TEXT_BLOCK_STRING_REQUIRED')
    return blocks


def normalized_bbox(block, image_width, image_height):
    """Return exact normalized geometry or reject; never clip invalid bounds."""
    bbox = block.get('bbox'); system = block['coordinate_system']
    if system == 'DOCLING_PDF_POINTS_WITH_DECLARED_ORIGIN':
        width, height = block['page_size']['width'], block['page_size']['height']
        if not isinstance(bbox, dict):
            raise ValueError('MISSING_DOCLING_BOX')
        left, right = bbox['l'], bbox['r']
        if bbox['coord_origin'] == 'BOTTOMLEFT':
            top, bottom = height - bbox['t'], height - bbox['b']
        elif bbox['coord_origin'] == 'TOPLEFT':
            top, bottom = bbox['t'], bbox['b']
        else:
            raise ValueError('UNKNOWN_COORDINATE_ORIGIN')
        values = [left / width, top / height, right / width, bottom / height]
    else:
        if bbox is None and block.get('polygon') is not None:
            polygon = block['polygon']; bbox = [min(p[0] for p in polygon), min(p[1] for p in polygon),
                                               max(p[0] for p in polygon), max(p[1] for p in polygon)]
        if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
            raise ValueError('MISSING_TEXT_BOX')
        values = list(bbox) if system == 'NORMALIZED_TOP_LEFT' else [bbox[0] / image_width, bbox[1] / image_height,
                                                                    bbox[2] / image_width, bbox[3] / image_height]
        if system not in {'NORMALIZED_TOP_LEFT', 'INPUT_IMAGE_PIXELS_TOP_LEFT'}:
            raise ValueError('UNKNOWN_COORDINATE_SYSTEM')
    if (any(type(value) not in (int, float) or not math.isfinite(value) for value in values)
            or not 0 <= values[0] < values[2] <= 1 or not 0 <= values[1] < values[3] <= 1):
        raise ValueError('INVALID_NORMALIZED_BOX')
    return values
