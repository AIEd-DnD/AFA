import helper_functions as AFA
import resources as rsrc
import student_response_repo as SRR

subject = "English"
level = "Primary 5"
question = " "
student_response = SRR.Pri_EL_Essay_8
error_tags = rsrc.ELLB_20

user_msg = AFA.assemble_prompt(subject, level, question, student_response, error_tags=error_tags)
response = AFA.get_annotations(user_msg)
print(response)
AFA.display_output(response)