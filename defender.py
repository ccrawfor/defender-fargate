import os
import sys
import pathlib 
import requests
import ruamel.yaml
YAML = ruamel.yaml.YAML
from collections import OrderedDict
CM = ruamel.yaml.CommentedMap
TS = ruamel.yaml.comments.TaggedScalar
CS = ruamel.yaml.comments.CommentedSeq

import json


class YamlUtil:

    def parsetags(loader, node):
        node.value = {
            ruamel.yaml.ScalarNode:   loader.construct_scalar,
            ruamel.yaml.SequenceNode: loader.construct_sequence,
            ruamel.yaml.MappingNode:  loader.construct_mapping,
        }[type(node)](node)
        node.tag = node.tag.replace(u'!Ref', 'Ref').replace(u'!', u'Fn::')
        return dict([ (node.tag, node.value) ])


    funcnames = [ 'ImportValue', 'Ref', 'Base64', 'FindInMap', 'GetAtt', 'GetAZs',
                'Join', 'Select', 'Split', 'Split', 'Sub', 'And', 'Equals', 'If',
                'Not', 'Or' ]

    for func in funcnames:
        ruamel.yaml.add_constructor(u'!' + func, parsetags, constructor=ruamel.yaml.SafeConstructor)

    _yaml = ruamel.yaml.YAML(typ="safe")
    _yaml.default_flow_style = False
    _yaml.explicit_start = False
    _yaml.preserve_quotes = True
    _yaml.indent(mapping=2, sequence=4, offset=2)
   # _yaml.Representer.add_representer(OrderedDict, _yaml.Representer.represent_dict)

    def __init__(self, yaml: YAML = _yaml):
        self.yaml = yaml
        

    def load_file(self, path):
        return self.yaml.load(path)

    def dump_file(self, data, path):
        self.yaml.dump(data, path)    
    

    def get_tasks(self, d: CM, family=""):
       # if isinstance(d, CM):
        if isinstance(d, dict):
           keys = [key for key in d.keys()]        
           if 'Resources' in keys:
                self.get_tasks(d['Resources'])
           else: 
                #if isinstance(d, CM):
                if isinstance(d, dict):
                    for key, value in d.items():
                        if value['Type'] == 'AWS::ECS::TaskDefinition':
                            self.update_tasks(value)   
                
    def update_tasks(self, d: CM):
        #get properties family
        #if isinstance(d['Properties']['Family'], TS):
        if isinstance(d['Properties']['Family'], dict):
            #Check for existense of properties
            #print(type(d['Properties']['ContainerDefinitions']))
            #if isinstance((d['Properties']['ContainerDefinitions']), CS):
            if isinstance((d['Properties']['ContainerDefinitions']), list):
                for i in (d['Properties']['ContainerDefinitions']):
                    #if isinstance(i, CM):
                    if isinstance(i, dict):    
                        keys = [key for key in i.keys()]
                        if 'DependsOn' in keys:
                            #if type(i['DependsOn']) is CS:
                            if type(i['DependsOn']) is dict:
                                i['DependsOn'].update({'Condition': 'START', 'ContainerName': 'TwistlockDefender'})
                                for i, value in enumerate(i['DependsOn']):
                                    pass
                                    #if type(value) is TS:
                                        #print(value.tag.value)
                                    
                           # print(type(i['DependsOn']))
                            #i['DependsOn'].insert({'Condition': 'START', 'ContainerName': 'TwistlockDefender'})
                            #print((i['DependsOn']))
                            #self.dump_file(i, sys.stdout)

           # print(len(d['Properties']['ContainerDefinitions']))
            
         
    def rec_sort(d):
        if isinstance(d, dict):
            res = ruamel.yaml.CommentedMap()
            for k in sorted(d.keys()):
                res[k] = rec_sort(d[k])
            return res
        if isinstance(d, list):
               for idx, elem in enumerate(d):
                    d[idx] = rec_sort(elem)
        return d

  
  

  # logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


   



# Open & parse CloudFormation Template
#print('Parsing CloudFormation Template')
data = YamlUtil().load_file(pathlib.Path(''))
#data = rec_sort(data)

YamlUtil.get_tasks(YamlUtil(), data)
YamlUtil().dump_file(data, sys.stdout)