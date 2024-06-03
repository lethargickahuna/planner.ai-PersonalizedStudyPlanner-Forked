import streamlit as st
import cohere
import datetime
import pandas as pd

# Fetch API key from Streamlit secrets
try:
    cohere_api_key = st.secrets["cohere"]["api_key"]
except KeyError as e:
    st.error(f"Missing secret: {e}. Please make sure your Streamlit secrets are configured correctly.")
    st.stop()

# Initialize Cohere client
cohere_client = cohere.Client(cohere_api_key)

# Function to generate study plan
def generate_study_plan(course_load, deadlines, preferences):
    prompt = f"Generate a study plan for the following courses: {course_load}. Deadlines are: {deadlines}. Preferences are: {preferences}."
    response = cohere_client.generate(prompt=prompt, max_tokens=300)
    return response.generations[0].text

# Function to parse deadlines
def parse_deadlines(deadlines):
    parsed_deadlines = []
    for deadline in deadlines:
        parsed_deadlines.append({'course': deadline['course'], 'date': deadline['date'].strftime('%Y-%m-%d')})
    return parsed_deadlines

# Function to send notification
def send_notification(message):
    st.write(message)  # Placeholder for actual notification logic

# Layout 1: Dashboard
def dashboard_view(course_load, deadlines, preferences, study_plan, deadlines_data):
    st.subheader('📅 Weekly Calendar View')
    df = pd.DataFrame(deadlines_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    st.write(df)

    st.subheader('📋 Upcoming Deadlines List')
    st.write(df.sort_index())

    st.subheader('📝 Study Plan Summary')
    st.write(study_plan)

# Layout 3: Combined View
def combined_view(course_load, deadlines, preferences, study_plan, deadlines_data):
    st.subheader('🔄 Visual Timeline and Checklist')

    st.write('## Timeline')
    for deadline in deadlines_data:
        course = deadline['course']
        date = deadline['date']
        days_left = (datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.datetime.now()).days
        st.write(f"{course}: {date} ({days_left} days left)")
    
    st.write('## Checklist')
    for idx, deadline in enumerate(deadlines_data):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.checkbox(f"{deadline['course']}: {deadline['date']}", key=f'checkbox_{idx}')
        with col2:
            if st.button('Delete', key=f'delete_{idx}'):
                del st.session_state.deadlines[idx]
                st.experimental_rerun()

# Main app layout
st.title('📚 Personalized Study Planner')
st.write('Generate a personalized study plan based on your courses, deadlines, and personal preferences.')

# Adding courses and deadlines dynamically
st.header('🗓️ Add Your Courses and Deadlines')

if 'deadlines' not in st.session_state:
    st.session_state.deadlines = []

def add_course():
    st.session_state.deadlines.append({'course': '', 'date': datetime.date.today()})

st.button('Add Course', on_click=add_course)

for idx, deadline in enumerate(st.session_state.deadlines):
    with st.expander(f'Course {idx+1}'):
        course = st.text_input(f'Course Name {idx+1}', key=f'course_{idx}', value=deadline['course'])
        date = st.date_input(f'Deadline Date {idx+1}', key=f'date_{idx}', value=deadline['date'])
        st.session_state.deadlines[idx]['course'] = course
        st.session_state.deadlines[idx]['date'] = date

# Input fields
st.header('📝 Input Your Study Preferences')
preferences = st.text_area('Personal Preferences (e.g., study in the morning, prefer short sessions)', placeholder='Enter any study preferences')


if st.button('Generate Study Plan'):
    if st.session_state.deadlines and preferences:
        course_load = [item['course'] for item in st.session_state.deadlines]
        parsed_deadlines = parse_deadlines(st.session_state.deadlines)
        study_plan = generate_study_plan(course_load, parsed_deadlines, preferences)
        combined_view(course_load, parsed_deadlines, preferences, study_plan, parsed_deadlines)
    else:
        st.error('Please fill in all the fields.')

# Footer with more info
st.markdown('---')
