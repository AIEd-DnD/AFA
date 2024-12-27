import LangFA_AFA_converter as LFA
import json

for i in range(13):
    ref_dict = LFA.LangFAjsonReader('Dataset/number_'+str(i+1)+'_ELLB.json')
    with open('Texts/text'+str(i+1)+'.txt', 'r') as file:
        text = file.read()
    AFA_template = LFA.convertAFA(ref_dict, text)
    with open('Texts/text_'+str(i+1)+'_AFA.txt', 'w') as file:
        file.write(str(AFA_template))
    print('File text_'+str(i+1)+'_AFA.txt has been created')
