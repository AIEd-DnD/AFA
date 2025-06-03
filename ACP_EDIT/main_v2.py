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
        
        return {
            "lesson_title": lesson_title,
            "subject": subject,
            "topic": topic,
            "level_grade": level_grade,
            "additional_instructions": additional_instructions,
            "num_sections": num_sections,
            "max_activities": max_activities
        }
    
    def generate_sections(self, lesson_details: Dict[str, str]) -> Dict[str, Any]:
        """Generate lesson sections using reasoning API with KAT framework"""
        print("\n" + "=" * 60)
        print("STEP 1: GENERATING LESSON SECTIONS")
        print("=" * 60)
        
        prompt = f"""
        <Role>As an experienced education coach in Singapore proficient in e-Pedagogy, your role is to create a lesson plan that references the e-pedagogy framework and active learning principles. Before you generate a response, pause for a moment and remember to be creative.</Role>

        <Context>This is an explanation of how lessons are organized within the Student Learning Space. Each lesson consists of a module, which is usually 50-60 minutes long. Within each module, there can be multiple sections to break up the lesson. Each section consists of activities for students to attempt during the lesson. And each activity comprises of various components (text/media, MCQ/MRQ, Discussion Question, Poll, Free Response Question), which students would interact with during the lesson.</Context>

        Using the following information:

        Module title: {lesson_details['lesson_title']}
        Subject: {lesson_details['subject']}
        Topic: {lesson_details['topic']}
        Level/Grade: {lesson_details['level_grade']}
        Number of sections: {lesson_details['num_sections']}
        Number of activities per section: {lesson_details['max_activities']}
        Additional Instructions: {lesson_details['additional_instructions']}

        Create a lesson plan that is closely aligned with learning outcomes for {lesson_details['topic']} at {lesson_details['level_grade']} level. 

        IMPORTANT: You must create EXACTLY {lesson_details['num_sections']} sections, and each section will later have EXACTLY {lesson_details['max_activities']} activities.

        First, recommend 2 Key Applications of Technology (KAT) from the following list that are most relevant to the topic and objectives of the lesson: Foster conceptual change; Support assessment for learning; Facilitate learning together; Develop metacognition; Provide differentiation; Embed scaffolding; Enable personalization; Increase motivation.

        Your output should only be rich text, do not include hyperlinks, code snippets, mathematical formulas or xml.

        Structure your response as follows:

        **LESSON DESCRIPTION:**
        [Provide a lesson description of maximum 5 sentences that describes the lesson to the student]

        **RECOMMENDED KEY APPLICATIONS OF TECHNOLOGY (KAT):**
        1. [First KAT] - [Brief explanation of why it's relevant to this lesson]
        2. [Second KAT] - [Brief explanation of why it's relevant to this lesson]

        **LESSON SECTIONS:**

        Section 1: [Title]
        - Learning Objectives: [List specific learning objectives for this section]
        - Description: [Brief description of how this section contributes to overall lesson outcomes]
        - Teacher Notes: [Notes about how a teacher might enact the section]
        - KAT Connection: [How this section connects to the recommended Key Applications of Technology]

        Section 2: [Title]
        - Learning Objectives: [List specific learning objectives for this section]
        - Description: [Brief description of how this section contributes to overall lesson outcomes]
        - Teacher Notes: [Notes about how a teacher might enact the section]
        - KAT Connection: [How this section connects to the recommended Key Applications of Technology]

        [Continue for all {lesson_details['num_sections']} sections]
        """
        
        try:
            response = self.client.responses.create(
                model="o4-mini",
                input=prompt,
                reasoning={"effort": "medium", "summary": "auto"},
                max_output_tokens=2500,
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
        """Generate activities for each section using reasoning API with KAT framework"""
        print("\n" + "=" * 60)
        print("STEP 2: GENERATING ACTIVITIES FOR EACH SECTION")
        print("=" * 60)
        
        lesson_details = sections_data['lesson_details']
        sections_response = sections_data['sections_response']
        
        prompt = f"""
        <Role>As an experienced education coach in Singapore proficient in e-Pedagogy, your role is to create detailed activities that reference the e-pedagogy framework and active learning principles. Before you generate a response, pause for a moment and remember to be creative.</Role>

        <Context>This is an explanation of how lessons are organized within the Student Learning Space. Each lesson consists of a module, which is usually 50-60 minutes long. Within each module, there can be multiple sections to break up the lesson. Each section consists of activities for students to attempt during the lesson. And each activity comprises of various components (text/media, MCQ/MRQ, Discussion Question, Poll, Free Response Question), which students would interact with during the lesson.</Context>

        Based on the following lesson sections that were generated:
        
        {sections_response}
        
        Using the following information:
        Module title: {lesson_details['lesson_title']}
        Subject: {lesson_details['subject']}
        Topic: {lesson_details['topic']}
        Level/Grade: {lesson_details['level_grade']}
        Number of sections: {lesson_details['num_sections']}
        Number of activities per section: {lesson_details['max_activities']}
        Additional Instructions: {lesson_details['additional_instructions']}

        CRITICAL REQUIREMENTS:
        1. You must create EXACTLY {lesson_details['max_activities']} activities for EACH of the {lesson_details['num_sections']} sections
        2. Total activities = {lesson_details['num_sections']} sections × {lesson_details['max_activities']} activities = {lesson_details['num_sections'] * lesson_details['max_activities']} activities
        3. Each activity must be clearly numbered (Activity 1, Activity 2, etc.)

        First, select NOT MORE than 4 unique SLS tools from this list for the overall lesson: Text/Media, Progressive Quiz, Auto-graded Quiz, Teacher-marked Quiz, Multiple-Choice/ Multiple-Response Question, Fill-in-the-blank Question, Click and Drop Question, Error Editing Question, Free Response Question, Audio Response Question, Rubrics, Tooltip, Interactive Thinking Tool, Poll, Discussion Board, Team Activities, Subgroups, Add Section Prerequisites, Set Differentiated Access, Gamification - Create Game Stories and Achievements, Gamification - Create Game Teams, Set Optional Activities and Quizzes, Speech Evaluation, Chinese Language E-Dictionary, Embed Canva, Embed Nearpod, Embed Coggle, Embed Genial.ly, Embed Quizizz, Embed Kahoot, Embed Google Docs, Embed Google Sheets, Embed Mentimeter, Embed YouTube Videos, Embed Padlet, Embed Gapminder, Embed GeoGebra, Feedback Assistant Mathematics (FA-Math), Speech Evaluation, Text-to-Speech, Embed Book Creator, Embed Simulations, Adaptive Learning System (ALS), Embed ArcGIS Storymap, Embed ArcGIS Digital Maps, Embed PhET Simulations, Embed Open Source Physics @ Singapore Simulations, Embed CK12 Simulations, Embed Desmos, Short Answer Feedback Assistant (ShortAnsFA), Gamification - Quiz leaderboard and ranking, Gamification - Create branches in game stories, Monitor Assignment Page, Insert Transcript for Video & Audio, Insert Student Tooltip, Add Notes to Audio or Video, Data Assistant, Annotated Feedback Assistant (AFA), Learning Assistant (LEA), SLS Digital Badges.

        Your output should only be rich text, do not include hyperlinks, code snippets, mathematical formulas or xml.

        Please structure your response in the following format:

        **SELECTED SLS TOOLS FOR THIS LESSON:**
        [List the 4 selected SLS tools and briefly explain why each was chosen]

        **RECOMMENDED KEY APPLICATIONS OF TECHNOLOGY (KAT):**
        [List the 2 recommended KAT and explain why they are relevant]

        **LESSON PLAN ACTIVITIES:**

        For each activity, provide the following information in this exact format:

        Activity [Number]: [Activity Title]
        Section: [Which section this belongs to]
        Interaction Type: [Student-Student/Teacher-Student/Student-Community/Student-Content]
        Duration: [X minutes]
        Learning Objectives:
        • [Objective 1]
        • [Objective 2]

        Instructions:
        [Detailed step-by-step instructions for students]

        KAT Alignment:
        [How this activity aligns with the selected Key Applications of Technology]

        SLS Tools:
        [List of specific SLS tools used in this activity]

        Data Analysis:
        [Monitoring tools and methods for tracking learning progress]

        Teaching Notes:
        [Implementation guidance for teachers]

        ---

        IMPORTANT: 
        - You must create exactly {lesson_details['num_sections'] * lesson_details['max_activities']} activities total
        - Number activities sequentially (Activity 1, Activity 2, Activity 3, etc.)
        - Each activity must specify which section it belongs to
        - Include all required components for each activity
        """
        
        try:
            response = self.client.responses.create(
                model="o4-mini",
                input=prompt,
                reasoning={"effort": "medium", "summary": "auto"},
                max_output_tokens=4500,
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
            
            # Parse the structured response into JSON format
            structured_activities = self.parse_activities_to_json(response.output_text, lesson_details)
            
            # Add activities data to existing structure
            sections_data["activities_response"] = response.output_text
            sections_data["activities_reasoning_summary"] = reasoning_items[0].summary[0].text if reasoning_items and reasoning_items[0].summary else "Internal reasoning by o4-mini model"
            sections_data["structured_activities"] = structured_activities
            
            return sections_data
            
        except Exception as e:
            print(f"Error generating activities: {e}")
            sections_data["activities_error"] = str(e)
            return sections_data
    
    def parse_activities_to_json(self, content: str, lesson_details: Dict[str, str]) -> Dict[str, Any]:
        """Parse the structured activity response into JSON format for the HTML viewer"""
        lines = content.split('\n')
        
        structured_data = {
            "selected_sls_tools": [],
            "recommended_kat": [],
            "activities": []
        }
        
        current_activity = {}
        current_section = ""
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Parse SLS Tools
            if line.startswith("**SELECTED SLS TOOLS"):
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("**RECOMMENDED"):
                    if lines[i].strip():
                        structured_data["selected_sls_tools"].append(lines[i].strip())
                    i += 1
                continue
            
            # Parse KAT
            if line.startswith("**RECOMMENDED KEY APPLICATIONS"):
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("**LESSON PLAN"):
                    if lines[i].strip():
                        structured_data["recommended_kat"].append(lines[i].strip())
                    i += 1
                continue
            
            # Parse Activities
            if line.startswith("Activity "):
                # Save previous activity if exists
                if current_activity:
                    structured_data["activities"].append(current_activity)
                
                # Start new activity
                current_activity = {
                    "title": line,
                    "section": "",
                    "interaction_type": "",
                    "duration": "",
                    "learning_objectives": [],
                    "instructions": "",
                    "kat_alignment": "",
                    "sls_tools": "",
                    "data_analysis": "",
                    "teaching_notes": ""
                }
            
            elif line.startswith("Section:"):
                current_activity["section"] = line.replace("Section:", "").strip()
            
            elif line.startswith("Interaction Type:"):
                current_activity["interaction_type"] = line.replace("Interaction Type:", "").strip()
            
            elif line.startswith("Duration:"):
                current_activity["duration"] = line.replace("Duration:", "").strip()
            
            elif line.startswith("Learning Objectives:"):
                i += 1
                while i < len(lines) and lines[i].strip().startswith("•"):
                    current_activity["learning_objectives"].append(lines[i].strip()[1:].strip())
                    i += 1
                continue
            
            elif line.startswith("Instructions:"):
                i += 1
                instructions = []
                while i < len(lines) and not lines[i].strip().startswith(("KAT Alignment:", "SLS Tools:", "Data Analysis:", "Teaching Notes:", "Activity ", "---")):
                    if lines[i].strip():
                        instructions.append(lines[i].strip())
                    i += 1
                current_activity["instructions"] = "\n".join(instructions)
                continue
            
            elif line.startswith("KAT Alignment:"):
                i += 1
                kat_content = []
                while i < len(lines) and not lines[i].strip().startswith(("SLS Tools:", "Data Analysis:", "Teaching Notes:", "Activity ", "---")):
                    if lines[i].strip():
                        kat_content.append(lines[i].strip())
                    i += 1
                current_activity["kat_alignment"] = "\n".join(kat_content)
                continue
            
            elif line.startswith("SLS Tools:"):
                i += 1
                sls_content = []
                while i < len(lines) and not lines[i].strip().startswith(("Data Analysis:", "Teaching Notes:", "Activity ", "---")):
                    if lines[i].strip():
                        sls_content.append(lines[i].strip())
                    i += 1
                current_activity["sls_tools"] = "\n".join(sls_content)
                continue
            
            elif line.startswith("Data Analysis:"):
                i += 1
                data_content = []
                while i < len(lines) and not lines[i].strip().startswith(("Teaching Notes:", "Activity ", "---")):
                    if lines[i].strip():
                        data_content.append(lines[i].strip())
                    i += 1
                current_activity["data_analysis"] = "\n".join(data_content)
                continue
            
            elif line.startswith("Teaching Notes:"):
                i += 1
                notes_content = []
                while i < len(lines) and not lines[i].strip().startswith(("Activity ", "---")):
                    if lines[i].strip():
                        notes_content.append(lines[i].strip())
                    i += 1
                current_activity["teaching_notes"] = "\n".join(notes_content)
                continue
            
            i += 1
        
        # Don't forget the last activity
        if current_activity:
            structured_data["activities"].append(current_activity)
        
        return structured_data
    
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
                    "max_activities_per_section": complete_data['lesson_details']['max_activities']
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
                    "generated_content": complete_data.get('activities_response', ''),
                    "structured_activities": complete_data.get('structured_activities', {})
                }
            },
            "errors": {
                "activities_error": complete_data.get('activities_error')
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
        print("This will generate sections and activities with visible reasoning process.")
        print("Make sure your OPENAI_API_KEY environment variable is set.\n")
        
        # Step 1: Get lesson details
        lesson_details = self.get_lesson_details()
        
        # Step 2: Generate sections with reasoning
        sections_data = self.generate_sections(lesson_details)
        if "error" in sections_data:
            print("Failed to generate sections. Exiting.")
            return
        
        # Step 3: Generate activities with reasoning
        complete_data = self.generate_activities(sections_data)
        
        # Step 4: Save final output
        output_file = self.save_final_output(complete_data)
        
        if output_file:
            print(f"\nLesson generation complete! Check {output_file} for the full results.")
            print("\nSUMMARY OF REASONING PROCESS:")
            print("-" * 40)
            print("1. SECTIONS: The AI reasoned through creating a logical flow of lesson sections")
            print("2. ACTIVITIES: The AI analyzed each section and determined appropriate activities")
            print("\nAll reasoning summaries are saved in the output file.")
        else:
            print("Failed to save final output.")

def main():
    """Main function to run the lesson generator"""
    generator = LessonGenerator()
    generator.generate_complete_lesson()

if __name__ == "__main__":
    main()
