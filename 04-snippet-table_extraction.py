# Adapted from https://levelup.gitconnected.com/text-extraction-from-a-table-image-using-pytesseract-and-opencv-3342870691ae
# Fazlur Rahman, 2020

import cv2 as cv
import numpy as np
import pytesseract
import os
import pandas as pd

# Set paths
basepath = os.path.dirname(os.path.realpath(__file__))
crop_path = os.path.join(basepath, 'Crops')
imgpath = os.path.join(basepath, 'PNG')

# Required functions

def preprocessing(img):

    cImage = np.copy(img)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    canny = cv.Canny(gray, 50, 150)

    return cImage,gray,canny

def rotate_image(image, angle):

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv.INTER_LINEAR)

    return result

def overlapping_filter(lines, sorting_index):
    filtered_lines = []

    lines = sorted(lines, key=lambda lines: lines[sorting_index])
    separation = 1
    for i in range(len(lines)):
            l_curr = lines[i]
            if(i>0):
                l_prev = lines[i-1]
                if ( (l_curr[sorting_index] - l_prev[sorting_index]) > separation):
                    filtered_lines.append(l_curr)
            else:
                filtered_lines.append(l_curr)

    return filtered_lines

def is_vertical(line):
    return line[0]==line[2]

def is_horizontal(line):
    return line[1]==line[3]

def linedetection(image):

    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3,3))
    image_process = cv.dilate(image, kernel, iterations=1)

    rho = 1
    theta = np.pi/180
    threshold = 50
    minLinLength = 350
    maxLineGap = 6
    linesP = cv.HoughLinesP(image_process, rho , theta, threshold, None, minLinLength, maxLineGap)

    horizontal_lines = []
    vertical_lines = []

    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            if (is_vertical(l)):
                vertical_lines.append(l)

            elif (is_horizontal(l)):
                horizontal_lines.append(l)
        horizontal_lines = overlapping_filter(horizontal_lines, 1)
        vertical_lines = overlapping_filter(vertical_lines, 0)

    return horizontal_lines, vertical_lines

def optimise_position(canny,pageimg):

    angles = [round(x * 0.1,2) for x in range(-5, 5)]
    horizontal_anchors = []

    for degree in angles:

        image = rotate_image(canny,degree)
        horizontal_lines, vertical_lines = linedetection(image)
        horizontal_anchors.append(len(horizontal_lines))

    max_value = max(horizontal_anchors)
    max_index = horizontal_anchors.index(max_value)
    optimal_angle = angles[max_index]
    print('Identified optimal rotation angle:',optimal_angle)

    # Optimise grid + draw lines
    image = rotate_image(canny,optimal_angle)
    horizontal, vertical = linedetection(image)

    horizontal = []
    vertical = []

    h_left = []
    h_right = []
    v = []
    v_left = []
    v_right = []

    for line in horizontal_lines:
        h_left.append(line[0])
        h_right.append(line[2])
        v.append(line[1])

    for line in vertical_lines:
        v_left.append(line[0])
        v_right.append(line[2])

    for line in horizontal_lines:
        line[0] = min(h_left)

        if v_left:
            if min(v_left) < min(h_left):
                line[0] = min(v_left)

        line[2] = max(h_right)

        if v_right:
            if min(v_right) < min(h_left):
                line[2] = min(v_right)

        horizontal.append(line)

        cv.line(cImage, (line[0], line[1]), (line[2], line[3]), (0,255,0), 3, cv.LINE_AA)

    for line in vertical_lines:
        line[1] = min(v)
        line[3] = max(v)
        vertical.append(line)

        cv.line(cImage, (line[0], line[1]), (line[2], line[3]), (0,0,255), 3, cv.LINE_AA)

    crop_path = os.path.join(basepath, 'Crops')
    filename = os.path.join(crop_path, pageimg+'_slice.png')
    cv.imwrite(filename, cImage)
    return optimal_angle,horizontal,vertical

def get_cropped_image(image, x, y, w, h):
    cropped_image = image[ y:y+h , x:x+w ]
    return cropped_image

def get_ROI(pagefile,image, horizontal, vertical, left_line_index, right_line_index, top_line_index, bottom_line_index, offset=0):
    x1 = vertical[left_line_index][2] + offset
    y1 = horizontal[top_line_index][3] + offset
    x2 = vertical[right_line_index][2] - offset
    y2 = horizontal[bottom_line_index][3] - offset

    w = x2 - x1
    h = y2 - y1

    cropped_image = get_cropped_image(image, x1, y1, w, h)

    crop_path = os.path.join(basepath, 'Crops')
    filename = os.path.join(crop_path, pagefile+'_'+str(top_line_index)+'_'+str(left_line_index)+'.png')
    cv.imwrite(filename, cropped_image)

    return cropped_image

if __name__ == "__main__":

    # Get image file with table
    pagefile = 'USArmy-ELO-weeklyreports2005-6_0142.png'
    filestem = pagefile.split('_')[0]
    imgloc= os.path.join(imgpath, pagefile)
    img = cv.imread(cv.samples.findFile(imgloc))
    pageimg = imgloc.split('_')[1].split('.png')[0]

    data = [] # Empty data var

    # Pre-processes image
    cImage,gray,canny = preprocessing(img)

    # Rotates image to find optimal angle
    optimal_angle,horizontal,vertical = optimise_position(canny,pageimg)

    (thresh, bw) = cv.threshold(gray, 100, 255, cv.THRESH_BINARY)

    # If horizontal/vertical lines
    if len(horizontal) > 0 and len(vertical) > 0:

        print('Table detected, page angled at',optimal_angle)

        for row in range(0,10):

            column_entry = {'filename':pageimg}

            for column in range(0,5):

                try:

                    # Crop the table image
                    ROI_crop = get_ROI(pageimg,bw,horizontal,vertical,column,column+1,row,row+1)

                    # Use image to text
                    custom_config = r'--oem 3 --psm 6'
                    text = pytesseract.image_to_string(ROI_crop, lang="eng", config=custom_config)

                    text = text.replace('\n',' ')
                    text = text.replace('\x0c',' ')

                    # Generate table entry
                    try:
                        colname = inst['table_columns'][column]
                    except:
                        colname = 'col_'+str(column)

                    column_entry[colname] = text

                except:
                    pass

            if column_entry != {'filename':pagefile}:
                data.append(column_entry)

        # Write to datafile
        datafile = os.path.join(basepath, 'table_extract'+filestem+'.csv')
        datatowrite = pd.DataFrame(data)
        datatowrite.to_csv(datafile,sep=',',index=False)
