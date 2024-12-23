import docx2python as d2p
import resources as rsrc

AFA_template = {'annotated_response': None,'feedback_list':list()}
mapping = rsrc.old_to_new_error_mapping
with d2p.docx2python('Dataset/test_doc.docx') as docx:
    working_list = docx.comments
    old_error_tag = True
    feedback_list = list()
    working_length = len(working_list)
    for index in range(working_length):
        if index % 2 == 0:
            annotation_template = {'id': None, 'phrase': None, 'error_tag':[{'errorType': None}], 'comment': None}
            annotation_template['id'] = int((index/2) + 1)
            annotation_template['phrase'] = working_list[index][0]
            if old_error_tag == True:
                annotation_template['error_tag'][0]['errorType'] = mapping[working_list[index][3]]
            else:
                annotation_template['error_tag'][0]['errorType'] = working_list[index][3]
            annotation_template['comment'] = working_list[index+1][3]
            feedback_list.append(annotation_template)

    counter = 0
    annotated_response = str()    
    for para in docx.body_runs[0][0][0]:
        for phrase in para:
            if counter < len(feedback_list):
                if phrase == feedback_list[counter]['phrase']:
                    annotated_response += '<tag id="' + str(feedback_list[counter]['id']) + '">'
                    annotated_response += phrase
                    annotated_response += '</tag>'
                    counter += 1
                else:
                    annotated_response += phrase
            else:
                annotated_response += phrase

AFA_template['annotated_response'] = annotated_response
AFA_template['feedback_list'] = feedback_list
print(AFA_template)