import pandas as pd
import os
import nltk
from nltk.corpus import stopwords
import re

stop_words = set(stopwords.words('english'))

# Set paths
basepath = os.path.dirname(os.path.realpath(__file__))
textpath = os.path.join(basepath, 'TXT')
extractedpath = os.path.join(basepath, 'Data')

# Instruction dictionary (in project stored in a separate file)
instructions = [{

    'filename': 'USMC-ELOreport-May2011.pdf',
    'ignorepages': [],

    'date_patterns': [
        ('-(.*?)\*', [(0, 9999)]),
        ('-(.*?)NOTICE', [(0, 9999)])
    ],

    'type_patterns': [
        ('MOVIE PROJECTS', [(0, 9999)]),
        ('TELEVISION PROJECTS', [(0, 9999)]),
        ('DOCUMENTARIES', [(0, 9999)]),
        ('VIDEO GAMES', [(0, 9999)]),
        ('PROJECTS COMPLETE', [(0, 9999)]),
        ('DENIED REQUESTS', [(0, 9999)]),
        ('PENDING AIR DATE', [(0, 9999)])
    ],

    'title_patterns': [
        ('“(.*?)”\s*—', [(0, 9999)]),
        ('“(.*?)”\s*-', [(0, 9999)]),
        ('"(.*?)"\s*\(.*\)\s*-', [(0, 9999)])
    ],

    'studio_patterns': [
        ('-(.*?):', [(0, 9999)]),
    ],

    'replacements': [
        ('Shorts" - DoD', 'Shorts" - : DoD')
    ]
}]

# Required functions

def pattern_parse(pattern_name,previous,sentence,n,page):

    outcome = previous # Set previous value as default

    # Loop through relevant patterns
        # Check page interval (second and third element in tuple)

    for p in instructions[n][pattern_name]:
        for pagerange in p[1]:
            if page >= pagerange[0] and page <= pagerange[1]:

                # Regex pattern (first element in tuple)
                regexpattern = p[0]

                # Match regex pattern
                info_extract = re.findall(regexpattern, sentence)

                # If found match: update outcome and break
                if info_extract:
                    outcome = info_extract[0]
                    sentence = sentence.replace(outcome,'')

                    return outcome.strip(),sentence,'changed' # Return update outcome

                    break # Break out of loop

    return outcome,sentence,'unchanged' # Return previous outcome

def parsing(instructions):

    for n,f in enumerate(instructions):

        # Set page start sequence:
        beginpage = '#<# EXTRACTED PAGE START (.*?) #>#'

        filename = f['filename']
        data = [] # Set empty list var

        print('\nStart parsing file',n+1,'out of',len(instructions),'-',filename)

        # Change into txt extension
        filenametxt = filename.replace('.pdf','.txt')

        # Define file location
        sourceloc = os.path.join(textpath, filenametxt)

        # Read file contents into variable text
        with open(sourceloc, 'r') as file:
            text = file.read()

        # Set empty variables
        page = 0
        date = type = title = studio = ''

        # Loop through text variable, line by line
            # Loop through line, sentence by sentence

        for line in text.splitlines():

            ### Do replacements...

            for rpl in instructions[n]['replacements']:
                line = re.sub(rpl[0],rpl[1], line)

            for sentence in line.split('. '):

                # Reset title and studio when an empty line is encountered
                if sentence == '':
                    title = studio = ''

            ### INFER PAGE

                # Look for page header in each sentence
                page_extract = re.findall(beginpage, sentence)

                # Keep first element of page_extract if list is not empty
                if page_extract:
                    page = page_extract[0]
                    sentence = sentence.replace('#<# EXTRACTED PAGE START ' + str(page) + ' #>#','')
                    page = int(page)

                # Check if page needs to be skipped or not

                skip = 0
                for ignore in f['ignorepages']:
                    if ignore[0] <= page <= ignore[1]: skip = 1

                if skip == 0:

                    ### PATTERN DETECTION

                    date,sentence,status = pattern_parse('date_patterns',date,sentence,n,page)

                    if '{{{datebreak}}}' in sentence:
                        date = 'no date'

                    # A new date indicates a new document: reset type, title, studio to prevent false carry-over

                    if status == 'changed':
                        type = title = studio = ''

                    type,sentence,status = pattern_parse('type_patterns',type,sentence,n,page)

                    # A new type indicates a new section in the document: reset title, studio to prevent false carry-over

                    if status == 'changed':
                        title = studio = ''

                    title,sentence,status = pattern_parse('title_patterns',title,sentence,n,page)
                    studio,sentence,status = pattern_parse('studio_patterns',studio,sentence,n,page)

                ### Add to data variable

                    if title != '':

                        data.append({
                            'document':filename,
                            'page':page,
                            'date':date,
                            'title':title,
                            'studio':studio,
                            'type':type,
                            'text':sentence,
                        })

        ### Write data to file
        datafile = os.path.join(extractedpath, 'df_'+filename.replace('pdf','csv'))
        datatowrite = pd.DataFrame(data)
        datatowrite.to_csv(datafile,sep=',',index=False)
        print('Parsing',filename,'done')

if __name__ == "__main__":
    parsing(instructions)
