import sys,glob
from PIL import Image
pre=sys.argv[1]; cols=int(sys.argv[2]) if len(sys.argv)>2 else 2
fs=sorted(glob.glob(f'{pre}-*.png'))
ims=[Image.open(f) for f in fs]
w,h=ims[0].size; rows=(len(ims)+cols-1)//cols
sheet=Image.new('RGB',(w*cols,h*rows),'white')
for i,im in enumerate(ims): sheet.paste(im,((i%cols)*w,(i//cols)*h))
sheet.save(f'{pre}-sheet.png'); print(sheet.size, len(ims))
