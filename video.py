import cv2
import os
import argparse
import sys
from collections import Counter
from PIL import Image, ImageDraw
import glob

savepath = './temp/'
gscale=["@","#","S","%","?","*","+",";",":",",","."]

def img2ascii(img, wid):
    global width
    width = wid
    W,H = img.size
    ratio = H/(W*1.65)
    h = int(ratio*width)
    newimg = img.resize((width,h))
    greyimg = newimg.convert('L')
    pix=greyimg.getdata()
    character="".join([gscale[int(p/25)] for p in pix])
    return character

def resizetext(char, factor):
    arr = []
    for i in range (0,len(char),width):
        arr.append(list(char[i:width+i]))
    h = int(len(arr)/factor)
    w = int(len(arr[0])/factor)
    newarr = [[0]*w for i in range(h)]
    for i in range(h):
        for j in range(w):
            window = []
            for k in range(factor):
                for l in range(factor):
                    window.append(arr[(factor*i)+k][(factor*j)+l])
            occurence_count = Counter(window)
            del window
            newarr[i][j] = occurence_count.most_common(1)[0][0]
    return newarr

def main(path, outpath, color, detred, speed, quality, file = None):
    if file == None:
        return None
    images = []
    vidcap = cv2.VideoCapture(file)
    success,image = vidcap.read()
    count = 0
    while success:
        cv2.imwrite(savepath+'t'+(str(count)).zfill(4)+".jpg", image)   
        success,image = vidcap.read()
        count += 1
    first = Image.open(path+"t0000.jpg")
    w, h = first.size
    for img in os.listdir(path):
        image = Image.open(path+img)
        character = img2ascii(image, 100)
        arr = resizetext(character, detred)
        blank = Image.new('RGB', (1000, 1000), color = color[0])
        d = ImageDraw.Draw(blank)
        xpos = 0
        ypos = 0
        for i in arr:
            for j in i:
                d.text((xpos,ypos), j, fill=color[1])
                xpos += 7
            xpos = 0
            ypos+=10
        blank = blank.crop((0, 0, (7*len(arr[0])), ypos))
        w, h = blank.size
        blank = blank.resize((int(w*quality), int(h*quality)))
        blank.save(path+img)
    fp_in = path+"*.jpg"
    fp_out = outpath+"op.gif"
    img, *imgs = [Image.open(f) for f in sorted(glob.glob(fp_in))]
    img.save(fp=fp_out, format='GIF', append_images=imgs, save_all=True, duration=int(200/speed), loop=0)

if __name__=="__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--fn", help="filename for source.  Eg: 'Ros.mp4'")
    a.add_argument("--bg", help="background color RGB. Eg: '255,255,255'")
    a.add_argument("--fg", help="foreground color RGB. Eg: '0,0,0'")
    a.add_argument("--rd", help="reduce detail, 1 for no reduction, higher integers for reduction")
    a.add_argument("--sp", help="speedup factor, float values equal to or greater than 1")
    a.add_argument("--sz", help="sizing factor to control quality and gif storage size, float value between 0 and 1")
    args = a.parse_args()
    args = vars(args)
    print(args)
    bgcolor = tuple([int(i) for i in (args['bg'].split(','))])
    fgcolor = tuple([int(i) for i in (args['fg'].split(','))])
    main(file = args['fn'], path = "./temp/", outpath = './', color = [bgcolor, fgcolor], detred = int(args['rd']), speed = float(args['sp']), quality = float(args['sz']))
    for i in  os.listdir("./temp/"):
        os.remove("./temp/"+i)