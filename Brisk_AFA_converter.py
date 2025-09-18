import docx2python as d2p
import re

def extract_from_asterisks(text):
    """
    Extract text that is wrapped between a pair of asterisks.
    
    Args:
        text (str): Input string containing text with asterisks
        
    Returns:
        str: The text between asterisks, or None if no match found
    """
    # Pattern explanation:
    # \* - matches literal asterisk (escaped)
    # (.*?) - captures any characters (non-greedy)
    # \* - matches literal asterisk (escaped)
    pattern = r'\*(.*?)\*'
    
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None

def convert_docx_to_AFA(docx_path):
    AFA_template = {'annotated_response': None,'feedback_list':list()}
    with d2p.docx2python(docx_path) as docx:
        working_list = docx.comments

        feedback_list = list()
        working_length = len(working_list)
        for index in range(working_length):
            if index % 2 == 0:
                annotation_template = {'id': None, 'phrase': None, 'error_tag':[{'errorType': None}], 'comment': None}
                annotation_template['id'] = int((index/2) + 1)
                annotation_template['phrase'] = working_list[index][0]
                annotation_template['error_tag'][0]['errorType'] = extract_from_asterisks(working_list[index][3])
                annotation_template['comment'] = working_list[index][3]
                feedback_list.append(annotation_template)

        counter = 0
        annotated_response = str()    
        for para in docx.body_runs[0][0][0]:
            print(counter)
            print(para)
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
    final_name = docx_path[14:-5]
    with open('Output/'+ final_name +'.txt', 'w') as output:
        output.write(str(AFA_template))
    return AFA_template