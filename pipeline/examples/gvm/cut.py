"""ISNet で背景を切り抜く（rembg と同じ前処理）"""
import numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
_s = None
def cutout(path):
    global _s
    if _s is None: _s = ort.InferenceSession('/home/claude/models/isnet.onnx', providers=['CPUExecutionProvider'])
    im = Image.open(path).convert('RGB')
    x = np.asarray(im.resize((1024, 1024), Image.LANCZOS)).astype(np.float32) / 255.0
    x = (x - 0.5) / 1.0
    x = x.transpose(2, 0, 1)[None]
    y = _s.run(None, {_s.get_inputs()[0].name: x})[0][0, 0]
    y = (y - y.min()) / (y.max() - y.min() + 1e-9)
    m = Image.fromarray((y * 255).astype(np.uint8)).resize(im.size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(1))
    out = im.convert('RGBA'); out.putalpha(m)
    bb = m.point(lambda v: 255 if v > 40 else 0).getbbox()
    return out.crop(bb) if bb else out
