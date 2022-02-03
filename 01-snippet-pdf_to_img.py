from pdf2image import convert_from_path
import os

basepath = os.path.dirname(os.path.realpath(__file__))
pdfpath = os.path.join(basepath, 'PDF')
imgpath = os.path.join(basepath, 'PNG')

def pdftoimg(sourceloc):

    pages = convert_from_path(sourceloc, dpi=200, grayscale=True, transparent=True) # Convert PDF file into pages

    for i,page in enumerate(pages):

        imgfile = sourceloc.split('/')[-1].replace('.pdf', '_' + str(i+1).zfill(4) + '.png') # Set img file name
        imgfilename = os.path.join(imgpath,imgfile) # Set img file path
        page.save(imgfilename, 'PNG') # Save image

        print('Saved',i+1,'out of',len(pages),'page images')

if __name__ == "__main__":

    for filename in os.listdir(pdfpath):
        sourceloc = os.path.join(pdfpath, filename)
        pdftoimg(sourceloc)
