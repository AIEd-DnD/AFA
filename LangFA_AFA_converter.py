import json

def LangFAjsonReader(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def tagCreator(number_of_tags):
    list_of_Tags = ['</tag>'] 
    for i in range(number_of_tags):
        new_tag = '<tag id="' + str(i+1) + '">'
        list_of_Tags.append(new_tag)
    return list_of_Tags

def autoTagger(ref_dict, text):
    shift = 0
    no_of_cards = len(ref_dict['data'])
    tag_list = tagCreator(no_of_cards)
    for i in range(no_of_cards):
        start = ref_dict['data'][i]['data']['highlighterSelectors'][0]['start'] + shift
        end = ref_dict['data'][i]['data']['highlighterSelectors'][0]['end'] + shift
        front_tag = tag_list[i+1]
        text = text[:start] + front_tag + text[start:end] + tag_list[0] + text[end:] 
        shift_increment = len(front_tag) + len(tag_list[0])
        shift += shift_increment
    return text

def convertAFA(ref_dict, text):
    AFA_template = {'annotated_response': None,'feedback_list':list()}
    AFA_template['annotated_response'] = autoTagger(ref_dict, text)
    AFA_annotation_template = {'id': None, 'phrase': None, 'error_tag':[{'errorType': None}], 'comment': None}
    no_of_cards = len(ref_dict['data'])
    for i in range(no_of_cards):
        AFA_annotation_template['id'] = i+1
        AFA_annotation_template['phrase'] = ref_dict['data'][i]['data']['highlightedContent']
        AFA_annotation_template['error_tag'][0]['errorType'] = ref_dict['data'][i]['keywords']
        AFA_annotation_template['comment'] = ref_dict['data'][i]['note']
        AFA_template['feedback_list'].append(AFA_annotation_template)
        AFA_annotation_template = {'id': None, 'phrase': None, 'error_tag':[{'errorType': None}], 'comment': None}
    return AFA_template