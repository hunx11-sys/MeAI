# 장표 그림(JPEG) → PDF 한 파일
import json, sys
from PIL import Image
files = json.load(open(sys.argv[1]))
ims = [Image.open(f).convert('RGB') for f in files]
ims[0].save(sys.argv[2], save_all=True, append_images=ims[1:], resolution=216.0)
