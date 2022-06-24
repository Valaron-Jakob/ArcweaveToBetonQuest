import json
import yaml

quest_file_path     = input('Path of the questfile:        ')
quest_version       = input('BetonQuest version (2.0|1.X): ')
quest_use_titles    = input('Use titels (True|False):      ')
quester_name        = input('Name of the questNPC:         ')

with open(quest_file_path, 'r') as stream:
  data = json.load(stream)

quest_start_id  = data['startingElement']

conversation_format = {
    'quester': quester_name,
    'first': quest_start_id,
    'NPC_options': {},
    'player_options': {}
}

try:
    if quest_use_titles == "True":
        ids_to_titles = {}

        for key in data['elements'].keys():
            title = data['elements'][key]['title'].replace('<p>','').replace('</p>','')
            ids_to_titles[key] = title

            conversation_format['NPC_options'][title] = {
                'text': data['elements'][key]['content'].replace('<p>','').replace('</p>',''),
                'pointers': ','.join(data['elements'][key]['outputs'])
            }

        for key in data['connections'].keys():
            conversation_format['player_options'][key] = {
                'text': data['connections'][key]['label'].replace('<p>','').replace('</p>',''),
                'pointer': ids_to_titles[data['connections'][key]['targetid']]
            }

        conversation_format['first'] = ids_to_titles[quest_start_id]

    else:
        for key in data['elements'].keys():
            conversation_format['NPC_options'][key] = {
                'text': data['elements'][key]['content'].replace('<p>','').replace('</p>',''),
                'pointers': ','.join(data['elements'][key]['outputs'])
            }

        for key in data['connections'].keys():
            conversation_format['player_options'][key] = {
                'text': data['connections'][key]['label'].replace('<p>','').replace('</p>',''),
                'pointer': data['connections'][key]['targetid']
            }

    if quest_version == str(2.0):
        conversation_format = {
            'conversations': {
                quester_name.lower().replace(' ','_'): conversation_format.copy()
            }
        }

    output_path = quest_file_path.split('\\')
    output_path.pop()
    output_path = '\\'.join(output_path)

    with open(output_path + '\quest_conversation.yml', 'w', encoding='utf8') as outfile:
        yaml.dump(conversation_format, outfile, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print('FINISHED: The conversion was successful!')
    print('FINISHED: A file called "quest_conversation.yml" was created in the scripts folder.')

except:
    print('ERROR: The conversion was not successful!')