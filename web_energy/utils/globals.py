import os, sys

# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = sys.path[1]

TOOLS = [
    'codecarbon',
    'scaphandre'
]

CATEGORIES = [
    'age_restricted',
    'bakery',
    'content_sharing',
    'country_select',
    'e_commerce',
    'informational',
    'login',
    'marketing',
    'online_games',
    'search_engines',
    'social_media',
    'software_distribution',
    'streaming_audio',
    'streaming_video',
    'utilities'
]

LABELS = ['A', 'B', 'C', 'D', 'E', 'F', 'G']