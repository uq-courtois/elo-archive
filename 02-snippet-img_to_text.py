import os
import cv2
import pytesseract

# Set paths
basepath = os.path.dirname(os.path.realpath(__file__))
pdfpath = os.path.join(basepath, 'PDF')
imgpath = os.path.join(basepath, 'PNG')
textpath = os.path.join(basepath, 'TXT')

def imgtotext(imgfile):
    imgfilename = os.path.join(imgpath, imgfile)
    img = cv2.imread(imgfilename, 0)
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(img, lang="eng", config=custom_config)
    return text

def stitch_text(pagenum,text,pagetext):
    text = text + '\n\n#<# EXTRACTED PAGE START ' + str(pagenum) + ' #>#\n\n' + pagetext
    return text

if __name__ == "__main__":

    for pdffile in os.listdir(pdfpath):
        imgfiles = os.listdir(imgpath)
        imgfiles.sort()

        text = ''

        for imgfile in imgfiles:
            if pdffile.split('.pdf')[0] == imgfile.split('_')[0]:

                print('Converting',imgfile,'to text')

                # Get page number
                pagenum = imgfile.split('_')[-1].replace('.png','')

                # Convert image to text
                sourceloc = os.path.join(imgpath, imgfile)
                pagetext = imgtotext(imgfile)

                # Stitch together
                text = stitch_text(pagenum,text,pagetext)

                # Write to txt file
                targetloc = os.path.join(textpath, pdffile.replace('.pdf','.txt'))
                open(targetloc, "w", encoding='utf8').write(text)
