'''
Module for storing generalized utility functions
'''

def description_filter_text(tag):
    '''
    Used to filter retrieved description HTML data to usable parts.
    '''
    if tag.name == 'p':
        if not tag.text.strip():
            # Do not include empty <p> tags
            return False
        if tag.parent.name not in ['td']:
            # Don't duplicate tags from tables
            include = True
            for child in tag.children:
                # Don't include <p> tags with <img> objects in them
                if child.name == 'img':
                    include = False

            return include

    if tag.name in ['ul', 'ol', 'table']:
        # Generally include all <ul>, <ol>, and <table> tags (and their children)
        return True

    return False

def paginate(list_to_paginate, page_size=25):
    '''
    Split a list into sub-lists of size = page_size
    '''
    return [
        list_to_paginate[index:index + page_size]
        for index in range(0, len(list_to_paginate), page_size)
    ]

def format_image_src(image_src: str):
    '''
    Ensures properly accessible formatting for src images during imports
    '''
    if image_src.startswith('https:'):
        return image_src
    else:
        return 'https:' + image_src 