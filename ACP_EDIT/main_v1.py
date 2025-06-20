import json
import os
from openai import OpenAI
from typing import Dict, List, Any
from dotenv import load_dotenv
import openai

# Update path to find .env in parent directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path)
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)


class LessonGenerator:
    def __init__(self):
        # Initialize OpenAI client
        # Make sure to set your OPENAI_API_KEY environment variable
        self.client = openai.OpenAI(api_key=openai_api_key)
        
    def get_lesson_details(self) -> Dict[str, str]:
        """Get lesson details from user input"""
        print("=" * 60)
        print("LESSON GENERATOR - Please provide the following details:")
        print("=" * 60)
        
        lesson_title = input("1. Lesson Title: ")
        subject = input("2. Subject (e.g., Chemistry, Geography, Math): ")
        topic = input("3. Topic (specific topic to cover): ")
        level_grade = input("4. Level/Grade (e.g., Secondary 1, Grade 8): ")
        additional_instructions = input("5. Additional Instructions (optional - any specific requirements, learning objectives, or teaching approaches): ")
        
        print("\n" + "=" * 60)
        print("LESSON STRUCTURE CONFIGURATION:")
        print("=" * 60)
        
        # Get number of sections
        while True:
            try:
                num_sections = int(input("6. Number of sections (1-5): "))
                if 1 <= num_sections <= 5:
                    break
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get max activities per section
        while True:
            try:
                max_activities = int(input("7. Maximum activities per section (1-5): "))
                if 1 <= max_activities <= 5:
                    break
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get max components per activity
        while True:
            try:
                max_components = int(input("8. Maximum components per activity (3-10): "))
                if 3 <= max_components <= 10:
                    break
                else:
                    print("Please enter a number between 3 and 10.")
            except ValueError:
                print("Please enter a valid number.")
        
        return {
            "lesson_title": lesson_title,
            "subject": subject,
            "topic": topic,
            "level_grade": level_grade,
            "additional_instructions": additional_instructions,
            "num_sections": num_sections,
            "max_activities": max_activities,
            "max_components": max_components
        }
    
    def generate_sections(self, lesson_details: Dict[str, str]) -> Dict[str, Any]:
        """Generate lesson sections using reasoning API"""
        print("\n" + "=" * 60)
        print("STEP 1: GENERATING LESSON SECTIONS")
        print("=" * 60)
        
        prompt = f"""
        As an experienced {lesson_details['subject']} teacher, design a lesson flow comprising sections that helps {lesson_details['level_grade']} students achieve learning outcomes related to: {lesson_details['topic']}

        The title of the lesson is "{lesson_details['lesson_title']}" and the lesson should follow a structured learning sequence.

        Additional Instructions: {lesson_details['additional_instructions']}

        Design a lesson with exactly {lesson_details['num_sections']} sections that build upon each other logically.

        Your output should only be rich text, do not include hyperlinks, code snippets, mathematical formulas or xml.
        Your output should be a series of sections. For each section, provide (i) a title, (ii) notes about how a teacher might enact the section and other information that might be useful for the teacher when designing this section. You should also output a lesson description that describes the lesson to the student, the lesson description should be at most five sentences long.
        """
        
        try:
            response = self.client.responses.create(
                model="o4-mini",
                input=prompt,
                reasoning={"effort": "medium", "summary": "auto"},
                max_output_tokens=2000,
            )
            
            print("REASONING SUMMARY:")
            print("-" * 40)
            # Extract reasoning summary from the response
            reasoning_items = [item for item in response.output if item.type == 'reasoning']
            if reasoning_items and reasoning_items[0].summary:
                for summary in reasoning_items[0].summary:
                    print(summary.text)
            else:
                print("The AI is reasoning through the lesson structure internally...")
            
            print("\nSECTIONS GENERATED:")
            print("-" * 40)
            print(response.output_text)
            
            # Parse the response into structured format
            sections_data = {
                "lesson_details": lesson_details,
                "sections_response": response.output_text,
                "reasoning_summary": reasoning_items[0].summary[0].text if reasoning_items and reasoning_items[0].summary else "Internal reasoning by o4-mini model"
            }
            
            return sections_data
            
        except Exception as e:
            print(f"Error generating sections: {e}")
            return {"error": str(e)}
    
    def generate_activities(self, sections_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate activities for each section using reasoning API"""
        print("\n" + "=" * 60)
        print("STEP 2: GENERATING ACTIVITIES FOR EACH SECTION")
        print("=" * 60)
        
        lesson_details = sections_data['lesson_details']
        sections_response = sections_data['sections_response']
        
        prompt = f"""
        Based on the following lesson sections that were generated:
        
        {sections_response}
        
        As an experienced {lesson_details['subject']} teacher, design activities for each section that helps {lesson_details['level_grade']} students achieve learning outcomes related to: {lesson_details['topic']}

        Additional Instructions: {lesson_details['additional_instructions']}

        For each section identified above, suggest a maximum of {lesson_details['max_activities']} activities or quizzes. The activities and quizzes should help students understand the information in {lesson_details['topic']}. A quiz is a series of questions that students need to attempt, while an activity comprises of text, questions and other tasks for a student to complete.

        Your output should only be rich text, do not include hyperlinks, code snippets, mathematical formulas or xml.

        For each section, provide activities with: (i) a title, (ii) a description of the activity or quiz which summarises its objectives for the student, (iii) instructions for the activity or quiz that students should follow, (iv) other useful notes about the activity or quiz and details about how a teacher might enact it, (v) suggested time needed for a student to complete the activity or quiz.
        """
        
        try:
            response = self.client.responses.create(
                model="o4-mini",
                input=prompt,
                reasoning={"effort": "medium", "summary": "auto"},
                max_output_tokens=3000,
            )
            
            print("REASONING SUMMARY:")
            print("-" * 40)
            # Extract reasoning summary from the response
            reasoning_items = [item for item in response.output if item.type == 'reasoning']
            if reasoning_items and reasoning_items[0].summary:
                for summary in reasoning_items[0].summary:
                    print(summary.text)
            else:
                print("The AI is reasoning through the activities design internally...")
            
            print("\nACTIVITIES GENERATED:")
            print("-" * 40)
            print(response.output_text)
            
            # Add activities data to existing structure
            sections_data["activities_response"] = response.output_text
            sections_data["activities_reasoning_summary"] = reasoning_items[0].summary[0].text if reasoning_items and reasoning_items[0].summary else "Internal reasoning by o4-mini model"
            
            return sections_data
            
        except Exception as e:
            print(f"Error generating activities: {e}")
            sections_data["activities_error"] = str(e)
            return sections_data
    
    def generate_components(self, activities_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate components for each activity using reasoning API"""
        print("\n" + "=" * 60)
        print("STEP 3: GENERATING COMPONENTS FOR EACH ACTIVITY")
        print("=" * 60)
        
        lesson_details = activities_data['lesson_details']
        activities_response = activities_data['activities_response']
        
        prompt = f"""
        Based on the following activities that were generated:
        
        {activities_response}
        
        As an experienced {lesson_details['subject']} teacher, design exactly {lesson_details['max_components']} components for each activity that helps {lesson_details['level_grade']} students achieve learning outcomes related to: {lesson_details['topic']}

        Additional Instructions: {lesson_details['additional_instructions']}

        You should consider: Generate components to introduce and test the student's understanding for each activity mentioned above.

        There are only five types of components:
        1. A paragraph of text to help students understand the learning outcomes. The text can include explanations and examples to make it easier for students to understand the learning outcomes.
        2. A multiple choice question with four options of which only one option is correct
        3. A free response question which includes suggested answers
        4. A poll which is a multiple choice question with four options but no correct answer
        5. A discussion question which invites students to respond with their opinion

        Your output should only be rich text, do not include hyperlinks, code snippets, mathematical formulas or xml.

        For each activity, design exactly {lesson_details['max_components']} components. The first component should be an activity description that describes the activity to the student. The second component should be instructions to students on how to complete the activity. The rest of the components can be either text, multiple choice question, free response question, poll or discussion question.

        For each paragraph of text, provide (i) the required text, which can include tables or lists.
        For each multiple choice question, provide (i) the question, (ii) one correct answer, (iii) feedback for why the correct answer answers the question (iv) three distractors which are incorrect answers, (v) feedback for each distractor explaining why the distractor is incorrect and what the correct answer should be (vi) suggested time needed for a student to complete the question (vii) total marks for the question.
        For each free response question, provide (i) the question, (ii) total marks for the question, (iii) suggested answer, which is a comprehensive list of creditworthy points, where one point is to be awarded one mark, up to the total marks for the question, (iv) suggested time needed for a student to complete the question.
        For each poll, provide (i) a question, (ii) at least two options in response to the question.
        For each discussion question, provide (i) the discussion topic, (ii) a free response question for students to respond to.
        """
        
        try:
            response = self.client.responses.create(
                model="o4-mini",
                input=prompt,
                reasoning={"effort": "medium", "summary": "auto"},
                max_output_tokens=4000,
            )
            
            print("REASONING SUMMARY:")
            print("-" * 40)
            # Extract reasoning summary from the response
            reasoning_items = [item for item in response.output if item.type == 'reasoning']
            if reasoning_items and reasoning_items[0].summary:
                for summary in reasoning_items[0].summary:
                    print(summary.text)
            else:
                print("The AI is reasoning through the component design internally...")
            
            print("\nCOMPONENTS GENERATED:")
            print("-" * 40)
            print(response.output_text)
            
            # Add components data to existing structure
            activities_data["components_response"] = response.output_text
            activities_data["components_reasoning_summary"] = reasoning_items[0].summary[0].text if reasoning_items and reasoning_items[0].summary else "Internal reasoning by o4-mini model"
            
            return activities_data
            
        except Exception as e:
            print(f"Error generating components: {e}")
            activities_data["components_error"] = str(e)
            return activities_data
    
    def save_final_output(self, complete_data: Dict[str, Any]) -> str:
        """Save the complete lesson data to a JSON file"""
        filename = "complete_lesson_output.json"
        
        # Structure the final output
        final_output = {
            "lesson_metadata": {
                "title": complete_data['lesson_details']['lesson_title'],
                "subject": complete_data['lesson_details']['subject'],
                "topic": complete_data['lesson_details']['topic'],
                "level_grade": complete_data['lesson_details']['level_grade'],
                "additional_instructions": complete_data['lesson_details']['additional_instructions'],
                "lesson_structure": {
                    "num_sections": complete_data['lesson_details']['num_sections'],
                    "max_activities_per_section": complete_data['lesson_details']['max_activities'],
                    "max_components_per_activity": complete_data['lesson_details']['max_components']
                },
                "generation_timestamp": str(os.popen('date').read().strip())
            },
            "generation_process": {
                "step_1_sections": {
                    "reasoning_summary": complete_data.get('reasoning_summary', ''),
                    "generated_content": complete_data.get('sections_response', '')
                },
                "step_2_activities": {
                    "reasoning_summary": complete_data.get('activities_reasoning_summary', ''),
                    "generated_content": complete_data.get('activities_response', '')
                },
                "step_3_components": {
                    "reasoning_summary": complete_data.get('components_reasoning_summary', ''),
                    "generated_content": complete_data.get('components_response', '')
                }
            },
            "errors": {
                "activities_error": complete_data.get('activities_error'),
                "components_error": complete_data.get('components_error')
            }
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(final_output, f, indent=2, ensure_ascii=False)
            
            print(f"\n" + "=" * 60)
            print(f"FINAL OUTPUT SAVED TO: {filename}")
            print("=" * 60)
            
            return filename
            
        except Exception as e:
            print(f"Error saving final output: {e}")
            return ""
    
    def generate_complete_lesson(self):
        """Main method to generate the complete lesson"""
        print("LESSON GENERATOR WITH REASONING API")
        print("This will generate sections, activities, and components with visible reasoning process.")
        print("Make sure your OPENAI_API_KEY environment variable is set.\n")
        
        # Step 1: Get lesson details
        lesson_details = self.get_lesson_details()
        
        # Step 2: Generate sections with reasoning
        sections_data = self.generate_sections(lesson_details)
        if "error" in sections_data:
            print("Failed to generate sections. Exiting.")
            return
        
        # Step 3: Generate activities with reasoning
        activities_data = self.generate_activities(sections_data)
        
        # Step 4: Generate components with reasoning
        complete_data = self.generate_components(activities_data)
        
        # Step 5: Save final output
        output_file = self.save_final_output(complete_data)
        
        if output_file:
            print(f"\nLesson generation complete! Check {output_file} for the full results.")
            print("\nSUMMARY OF REASONING PROCESS:")
            print("-" * 40)
            print("1. SECTIONS: The AI reasoned through creating a logical flow of lesson sections")
            print("2. ACTIVITIES: The AI analyzed each section and determined appropriate activities")
            print("3. COMPONENTS: The AI designed specific components for each activity")
            print("\nAll reasoning summaries are saved in the output file.")
        else:
            print("Failed to save final output.")

def main():
    """Main function to run the lesson generator"""
    generator = LessonGenerator()
    generator.generate_complete_lesson()

if __name__ == "__main__":
    main()
