import json
import yaml

quest_file_path = "C:/Users/jakob/Desktop/ArcweaveToBetonQuest/convertable.json"
quester_name    = "Hildegart"
#quest_file_path     = input('Path of the questFile:        ')
#quester_name        = input('Name of the questNPC:         ')
#quest_use_titles    = input('Use titels (True|False):      ')
quester_name_snake  = quester_name.lower().replace(' ','_')

with open(quest_file_path, 'r') as stream:
  data = json.load(stream)

quest_start_id  = data['elements'][data['startingElement']]['title'].replace('<p>','').replace('</p>','')


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
def getComponentAttributes(data, component_key):
    attributes = []
    for key in data['components'][component_key]['attributes']:
        attr_name = data['attributes'][key]['name']
        attr_data = data['attributes'][key]['value']['data'].replace('<p>','').replace('</p>','')
        attributes.append(attr_name + ' ' + attr_data)
    return ','.join(attributes)

#Input the dataset and the desired folder name to get the folder element or NONE if the folder is not found
def getComponentFolder(data, folder_name):
    for key in data['components'].keys():
        if data['components'][key]['name'] == folder_name:
            folder = data['components'][key]
            return folder
    return None

#Input the dataset, the current element key and the folder string (events, conditions) to get a string of target component names
def getComponentPointers(data, element_key, folder):
    pointers = []
    for key in data['elements'][element_key]['components']:
        if key in getComponentFolder(data, folder)['children']:
            pointers.append(getComponentName(data, key))
    return ','.join(pointers)


class Quest:
    def __init__(self, name:str, quester:str, first:list, npc_options:dict, player_options:dict, conditions:dict, events:dict):
        self.name = name
        self.quester = quester
        self.first = first
        self.npc_options = npc_options
        self.player_options = player_options
        self.conditions = conditions
        self.events = events

    def getFormattedQuest(self):
        return {
            'conversations': {
                self.name: {
                    'quester': self.quester,
                    'first': ','.join(self.first),
                    'NPC_options': self.npc_options,
                    'player_options': self.player_options
                }
            },
            'conditions': self.conditions,
            'events': self.events
        }

    def setConvOptions(self, data:dict, npc_color:str, player_color:str):
        for key in data['elements']:
            option = ConvOption(data, key)

            if getElementTheme(data, key) == npc_color:
                self.npc_options.update(option.getFormattedOption())
            if getElementTheme(data, key) == player_color:
                self.player_options.update(option.getFormattedOption())
    
    def setConditions(self):
        for key in getComponentFolder(data, 'conditions')['children']:
            condition = Component(data, key)
            self.conditions.update(condition.getFormattedComp())
    
    def setEvents(self):
        for key in getComponentFolder(data, 'events')['children']:
            event = Component(data, key)
            self.events.update(event.getFormattedComp())

class ConvOption:
    def __init__(self, data:dict, key:str):
        self.key = key
        self.name = getElementName(data, key)
        self.text = getElementText(data, key)
        self.pointers = getElementPointers(data, key)
        self.conditions = getComponentPointers(data, key, 'conditions')
        self.events = getComponentPointers(data, key, 'events')
    
    def getFormattedOption(self):
        return {
            self.name: {
                'text': self.text,
                'pointers': self.pointers,
                'conditions': self.conditions,
                'events': self.events
            }
        }

class Component:
    def __init__(self, data:dict, key:str):
        self.key = key
        self.name = getComponentName(data, key)
        self.attributes = getComponentAttributes(data, key)

    def getFormattedComp(self):
        return {
            self.name: self.attributes
        }


quest = Quest(
    quester_name.lower().replace(' ','_'),
    quester_name,
    [getElementName(data, data['startingElement'])],
    {},
    {},
    {},
    {}
)

quest.setConvOptions(data, 'orange', 'lightBlue')
quest.setConditions()
quest.setEvents()


output_path = quest_file_path.split('/')
output_path.pop()
output_path = '/'.join(output_path)

with open(output_path + '/quest_conversation_2.yml', 'w', encoding='utf8') as outfile:
    yaml.dump(quest.getFormattedQuest(), outfile, default_flow_style=False, allow_unicode=True, sort_keys=False)