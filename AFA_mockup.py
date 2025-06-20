import helper_functions as AFA

print("Welcome to the AFA Mockup!")
print("You may use this to test AFA outputs after prompt refinement.")
print("Let's get started, shall we?")
print(" ")
subject = input("Subject: ")
level = input("Level: ")
question = input("Question Body: ")
student_response = input("Student's Response: ")
recipe = input("Describe how you would like the feedback to be presented: ")
suggested_answer = input("Enter your suggested answer (leave blank and press Enter if you are not using suggested answer): ")
rubrics = input("Enter your rubrics (leave blank and press Enter if you are not using rubrics): ")
error_tags = input("Enter your error tags with descriptions (leave blank and press Enter if you are not using error tags): ")
print(" ")

assembled_prompt = AFA.assemble_prompt(subject, level, question, student_response, recipe, suggested_answer, rubrics, error_tags)
raw_response = AFA.get_annotations(assembled_prompt)
display = AFA.display_output(raw_response)