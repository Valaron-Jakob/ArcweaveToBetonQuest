import json
#import yaml

quest_file_path     = input('Path of the questFile:        ')
quester_name        = input('Name of the questNPC:         ')
#quest_version       = input('BetonQuest version (2.0|1.X): ')
#quest_use_titles    = input('Use titels (True|False):      ')

with open(quest_file_path, 'r') as stream:
  data = json.load(stream)

quest_start_id  = data['startingElement']

conversation_format = {
    'quester': quester_name,
    'first': quest_start_id,
    'NPC_options': {},
    'player_options': {}
}

#Input the dataset and the desired folder name to get the folder element or NONE if the folder is not found
def getComponentFolder(data, folder_name):
    for key in data['components'].keys():
        if data['components'][key]['name'] == folder_name:
            folder = data['components'][key]
            return folder
        else:
            folder = None
    return folder

#Input the dataset and the current element to get a dict of target element keys and their respective titles
def getElementPointers(data, element_key):
    pointers = {}
    for key in element_key['outputs']:
        target_id = data['connections'][key]['targetid']
        pointers[target_id] = data['elements'][target_id]['title']
    return pointers

#Input the dataset, the current element and the folder (events, conditions) to get a dict of target keys and their respective titles
def getComponentPointers(data, element_key, folder):
    pointers = {}
    for key in element_key['components']:
        if key in getComponentFolder(data, folder)['children']:
            target_id = data['components'][key]
            pointers[target_id] = target_id['name']
    return pointers



conv_options = {}

for key in data['elements'].keys():
    conv_option_name = data['elements'][key]['title'].replace('<p>','').replace('</p>','')
    conv_option_text = data['elements'][key]['content'].replace('<p>','').replace('</p>','')

    conv_options[key] = {
        'conv_name': conv_option_name,
        'conv_text': conv_option_text,
        'pointers': getElementPointers(data, key),
        'events': getComponentPointers(data, key, 'events'),
        'conditions': getComponentPointers(data, key, 'conditions')
    }