import AFA_eval_functions as AFA
#import resources as rsrc
from datetime import datetime
import csv
import re

def start_new_compare_record(file_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Records/AFA_{file_name}_{timestamp}.csv"
    return filename

def write_into_compare_record(filename, data):
    header = ["Student's Response", "Annotated Response", "Cleaned Annotated Response", "Student Response Char Count", "Cleaned Annotated Response Char Count", "Char Count Difference", ]
    with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)
    print(f"CSV file '{filename}' has been created successfully.")

def extract_parameters(parameter_dict):
    students_response = parameter_dict['students_response']
    annotated_response = parameter_dict['annotated_response']
    return students_response, annotated_response

def strip_xml_tags(text):
    # This regex replaces tags like <tag id="1"> and </tag> with an empty string
    return re.sub(r'</?tag[^>]*>', '', text)


data = list()
compare_record = start_new_compare_record("compare_23lines")
print("The compare record has been created.")
compare_list = AFA.csv_to_list_of_dicts("Dataset/string_compare_sample.csv")
print("The compare list has been created.")

for compare_dict in compare_list:
    new_row = list()

    students_response, annotated_response = extract_parameters(compare_dict)
    new_row.append(students_response)
    new_row.append(annotated_response)

    cleaned_annotated_response = strip_xml_tags(annotated_response)
    new_row.append(cleaned_annotated_response)
    new_row.append(len(students_response))
    new_row.append(len(cleaned_annotated_response))
    new_row.append(len(students_response) - len(cleaned_annotated_response))

    data.append(new_row)

write_into_compare_record(compare_record, data)

#JSON_object = """
#{'annotated_response':'"Keep calm and love homework."-Anonymous. Homework is an essential tool in our lives, and many people get pressured and stressed by the overload of homework that they receive from their teachers over days some even going to the extent of crying. Homework was invented in 1905 by Robert Nevilin and is still very much present in today's modern schools. In my opinion, homework can be very useful to us and I do not agree with this statement. Many people complain that homework is useless. To begin with, homework is useful as it helps students learn to manage their time properly. Homework allows students to plan their time, so that they have sufficient time to study, do their homework, and also for leisure. The students will be able to learn how to put their homework as their first priority so that in the future, when they are working, they will be efficient and fast. However, there are also downsides to having homework. One may feel too stressed from keeping up deadlines and may not be able to cope with the enormous stress that they gain from it. Furthermore, homework can also help to improve one's grades, it can motivate students to continue studying and may even teach them a thing or two. In 2020, a research was conducted by Oxford University. They found out that 95 percent of students who consistently do their homework, do extraordinarily well in grades compared to students who are lazy and refuse to do their homework. In addition, homework also is a good way for revision. You can refer to it anytime you want one it has been marked and if there is any questions that needs to be clarified or, one may get wrong they can always ask the teacher how to solve the problem. Whatever homework students may not be able to do well in their studies and might not be motivated for school. Finally, homework is not a waste of time as without homework, many people will not be able to check if they are doing well in their studies or not. Homework helps to improve one's knowledge on the topic that they are doing and allows one to get better at it. If they are getting all the questions in the homework wrong, they will know which areas require improvements. From doing this, their grades will also improve and the students will be scoring higher marks compared to the homework as did not exist. Many people make the argument that people will have to sleep late if there is homework. However, if one has enough discipline and integrity, they will be able to finish their homework in time and be able to sleep early. In conclusion, homework is not a waste of time and it is very essential and useful in a student's life. Without it, many students may not be able to cope with their studies and eventually, their grades will dwindle.',
#'feedback_list':[{'id': 1, 'phrase': 'over days some even going to the extent of crying', 'error_tag': [{'errorType': 'Sentence'}], 'comment': 'This part of the sentence is confusing and lacks proper structure. Consider rephrasing it for clarity.'}, {'id': 2, 'phrase': 'a research was conducted', 'error_tag': [{'errorType': 'Noun'}], 'comment': "Use 'a study' or 'research was conducted' instead of 'a research was conducted'."}, {'id': 3, 'phrase': 'homework also is a good way', 'error_tag': [{'errorType': 'Word order'}], 'comment': "The word order is awkward. Consider rephrasing to 'homework is also a good way'."}, {'id': 4, 'phrase': 'anytime you want one it has been marked', 'error_tag': [{'errorType': 'Sentence'}], 'comment': 'This sentence is unclear. Consider rephrasing for better clarity.'}, {'id': 5, 'phrase': 'if there is any questions that needs', 'error_tag': [{'errorType': 'Noun'}], 'comment': "Use 'are' instead of 'is' to match the plural noun 'questions'."}, {'id': 6, 'phrase': 'Whatever homework students may not be able to do well', 'error_tag': [{'errorType': 'Sentence'}], 'comment': 'This sentence is incomplete and unclear. Consider revising it.'}, {'id': 7, 'phrase': 'compared to the homework as did not exist', 'error_tag': [{'errorType': 'Sentence'}], 'comment': 'This part of the sentence is confusing. Consider rephrasing it for clarity.'}]
#"""

#assembled_prompt = rsrc.AFA_JSON_correction_prompt.format(
    #JSON_object=JSON_object
#)

#response = AFA.get_annotations(assembled_prompt)
#response_dict = AFA.string_to_dict(response)
#annotated_response = response_dict['annotated_response']
#print(annotated_response)
#print(" ")
#print("Annotated Response:")
#print(strip_xml_tags(annotated_response))