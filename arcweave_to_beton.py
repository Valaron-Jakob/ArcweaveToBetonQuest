import json
import yaml

#quest_file_path     = "C:\\Users\\jakob\\Desktop\\ArcweaveToBetonQuest\\convertable.json"
quest_file_path     = input('Path of the questFile:        ')
quester_name        = input('Name of the questNPC:         ')
#quest_use_titles    = input('Use titels (True|False):      ')
quester_name_snake  = quester_name.lower().replace(' ','_')

with open(quest_file_path, 'r') as stream:
  data = json.load(stream)

quest_start_id  = data['elements'][data['startingElement']]['title'].replace('<p>','').replace('</p>','')


#Input the dataset and the desired folder name to get the folder element or NONE if the folder is not found
def getComponentFolder(data, folder_name):
    for key in data['components'].keys():
        if data['components'][key]['name'] == folder_name:
            folder = data['components'][key]
            return folder
    return None


#Get the name to a corresponding element key
def getElementName(data, element_key):
    return data['elements'][element_key]['title'].replace('<p>','').replace('</p>','')

#Get the text to a corresponding element key
def getElementText(data, element_key):
    return data['elements'][element_key]['content'].replace('<p>','').replace('</p>','')

#Get the theme to a corresponding element key
def getElementTheme(data, element_key):
    return data['elements'][element_key]['theme']

#Input the dataset and the current element key to get a string of target element names
def getElementPointers(data, element_key):
    pointers = []
    for key in data['elements'][element_key]['outputs']:
        pointers.append(getElementName(data, data['connections'][key]['targetid']))
    return ','.join(pointers)

#Get the name to a corresponding component key
def getComponentName(data, component_key):
    return data['components'][component_key]['name'].replace('<p>','').replace('</p>','')

#Input the dataset, the current element key and the folder string (events, conditions) to get a string of target component names
def getComponentPointers(data, element_key, folder):
    pointers = []
    for key in data['elements'][element_key]['components']:
        if key in getComponentFolder(data, folder)['children']:
            pointers.append(getComponentName(data, key))
    return ','.join(pointers)


#Input the dataset and a folder string (events, conditions) to get a dict of components
def getFullComponents(data, folder):
    components = {}
    for key in getComponentFolder(data, folder)['children']:
        attributes = {}
        for at_key in data['components'][key]['attributes']:
            attributes[at_key] = {
                'attribute_mechanism': data['attributes'][at_key]['name'],
                'attribute_input': data['attributes'][at_key]['value']['data'].replace('<p>','').replace('</p>','')
            }

        components[key] = {
            'component_name': data['components'][key]['name'],
            'component_attributes': attributes
        }
    return components


#Conversation file preset
conversation_format = {
    'conversations': {
        quester_name_snake: {
            'quester': quester_name,
            'first': quest_start_id,
            'NPC_options': {},
            'player_options': {}
        }
    },
    'conditions': getFullComponents(data, 'conditions'),
    'events': getFullComponents(data, 'events')
}


class Conversation:
    def __init__(self, name: str, quester: str, first: list, npc_options: list, player_options: list):
        self.name = name
        self.quester = quester
        self.first = first
        self.npc_options = npc_options
        self.player_options = player_options

    def getFormattedConv(self):
        return {
            self.name: {
                'quester': self.quester,
                'first': ','.join(self.first),
                'NPC_options': self.npc_options,
                'player_options': self.player_options
            }
        }

    def setConvOptions(self, data: dict, npc_color: str, player_color: str):
        for key in data['elements']:
            option = ConvOption(
                key, 
                getElementName(data, key),
                getElementText(data, key),
                getElementPointers(data, key),
                getComponentPointers(data, key, 'conditions'),
                getComponentPointers(data, key, 'events')
            )

            if getElementTheme(data, key) == npc_color:
                self.npc_options = self.npc_options.append(option)
            if getElementTheme(data, key) == player_color:
                self.player_options = self.player_options.append(option)

class ConvOption:
    def __init__(self, key: str, name: str, text: str, pointers: str, conditions: str, events: str):
        self.key = key
        self.name = name
        self.text = text
        self.pointers = pointers
        self.conditions = conditions
        self.events = events
    
    def getFormattedOption(self):
        return {
            self.name: {
                'text': self.text,
                'pointers': self.pointers,
                'conditions': self.conditions,
                'events': self.events
            }
        }


conversation = Conversation(
    quester_name.lower().replace(' ','_'),
    quester_name,
    data['elements'][data['startingElement']],
    [],
    []
)

conversation.setConvOptions()









#Final conversation parser
def getFinalConversation(input_conv):
    output_conv = {}
    for key in input_conv.keys():
        conv_name       = input_conv[key]['conv_name']
        conv_text       = input_conv[key]['conv_text']
        conv_pointers   = []
        conv_events     = []
        conv_conditions = []
        for pointer in input_conv[key]['pointers'].keys():
            conv_pointers.append(input_conv[key]['pointers'][pointer])
        conv_pointers = ','.join(conv_pointers)
        for event in input_conv[key]['events'].keys():
            conv_events.append(input_conv[key]['events'][event])
        conv_events = ','.join(conv_events)
        for condition in input_conv[key]['conditions'].keys():
            conv_conditions.append(input_conv[key]['conditions'][condition])
        conv_conditions = ','.join(conv_conditions)

        output_conv[conv_name] = {
            'text': conv_text,
            'pointers': conv_pointers,
            'events': conv_events,
            'conditions': conv_conditions
        }
    return output_conv


#Final component parser
def getFinalComponents(input_component):
    output_component = {}
    for key in input_component.keys():
        component_name  = input_component[key]['component_name']
        component_attributes = []
        for attribute in input_component[key]['component_attributes'].keys():
            component_attributes.append(input_component[key]['component_attributes'][attribute]['attribute_mechanism'] + " " + input_component[key]['component_attributes'][attribute]['attribute_input'])
        component_attributes = ','.join(component_attributes)

        output_component[component_name] = component_attributes
    return output_component


#Final file preset
final_format = {
    'conversations': {
        quester_name_snake: {
            'quester': quester_name,
            'first': quest_start_id,
            'NPC_options': getFinalConversation(conversation_format['conversations'][quester_name_snake]['NPC_options']),
            'player_options': getFinalConversation(conversation_format['conversations'][quester_name_snake]['player_options'])
        }
    },
    'conditions': getFinalComponents(conversation_format['conditions']),
    'events': getFinalComponents(conversation_format['events'])
}




#print(conv_options)

output_path = quest_file_path.split('\\')
output_path.pop()
output_path = '\\'.join(output_path)

with open(output_path + '\quest_conversation.yml', 'w', encoding='utf8') as outfile:
    yaml.dump(final_format, outfile, default_flow_style=False, allow_unicode=True, sort_keys=False)