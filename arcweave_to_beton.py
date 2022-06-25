import json
import yaml

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
    for key in data['elements'][element_key]['outputs']:
        target_id = data['connections'][key]['targetid']
        pointers[target_id] = data['elements'][target_id]['title'].replace('<p>','').replace('</p>','')
    return pointers

#Input the dataset, the current element and the folder (events, conditions) to get a dict of target keys and their respective titles
def getComponentPointers(data, element_key, folder):
    pointers = {}
    for key in data['elements'][element_key]['components']:
        if key in getComponentFolder(data, folder)['children']:
            pointers[key] = data['components'][key]['name'].replace('<p>','').replace('</p>','')
    return pointers


#Construct a dict with all the conversation options and needed data
conv_options = {}

for key in data['elements'].keys():
    conv_option_name = data['elements'][key]['title'].replace('<p>','').replace('</p>','')
    conv_option_text = data['elements'][key]['content'].replace('<p>','').replace('</p>','')
    conv_option_theme = data['elements'][key]['theme']

    conv_options[key] = {
        'conv_name': conv_option_name,
        'conv_text': conv_option_text,
        'conv_theme': conv_option_theme,
        'pointers': getElementPointers(data, key),
        'events': getComponentPointers(data, key, 'events'),
        'conditions': getComponentPointers(data, key, 'conditions')
    }


npc_color       = 'orange'
player_color    = 'lightBlue'

for key in conv_options.keys():
    if conv_options[key]['conv_theme'] == npc_color:
        conversation_format['NPC_options'][key] = conv_options[key]
    if conv_options[key]['conv_theme'] == player_color:
        conversation_format['player_options'][key] = conv_options[key]

#print(conv_options)

output_path = quest_file_path.split('\\')
output_path.pop()
output_path = '\\'.join(output_path)

with open(output_path + '\quest_conversation.yml', 'w', encoding='utf8') as outfile:
    yaml.dump(conversation_format, outfile, default_flow_style=False, allow_unicode=True, sort_keys=False)