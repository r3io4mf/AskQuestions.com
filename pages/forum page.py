# a python file inside pages 
import pandas as pd
from PIL import Image
import io
import os
import streamlit as st
import streamlit_authenticator as stauth
import yaml
import uuid

st.markdown('Forum Page 🖊️')
st.sidebar.markdown('Forum Page 🖊️')
# Login Page function
def Login():
    file_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(file_path) as file:
        config = yaml.load(file, Loader=yaml.loader.SafeLoader)
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    authenticator.login()
    if st.session_state["authentication_status"]:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
        st.session_state["mail"] = config['credentials']['usernames'][st.session_state['name']]['email']
        st.write(st.session_state["mail"])
        st.query_params['mode'] = 'ask'


    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')

    try:
        email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=False)
        if email_of_registered_user:
            st.success('User registered successfully')
            with open('../config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            # checks the email of all possible registered users to their subject combis
    except Exception as e:
        st.error(e)
# Function to load existing questions and replies (if any)
def load_data():
    if not os.path.exists('questions.csv'):
        questions_df = pd.DataFrame(columns=['Question', 'Image', 'Subject', 'Topic', 'Votes','id','starred'])
        questions_df.to_csv('questions.csv', index=False)
    else:
        questions_df = pd.read_csv('questions.csv')
        if 'Votes' not in questions_df.columns:
            questions_df['Votes'] = 0  # Add Votes column if it doesn't exist
            questions_df.to_csv('questions.csv', index=False)

    if not os.path.exists('replies.csv'):
        replies_df = pd.DataFrame(columns=['Question_ID', 'Reply', 'Image', 'Video'])
        replies_df.to_csv('replies.csv', index=False)
    else:
        replies_df = pd.read_csv('replies.csv')

    return questions_df, replies_df
# Function to save new question
def save_question(question, image, topic, subject):
    questions_df, _ = load_data()
    new_question = pd.DataFrame({'Question': [question], 'Image': [image], 'Subject': [subject],
                                  'Topic': [topic], 'Votes': [0],'id':[uuid.uuid4()], 'starred':[False]})
    questions_df = pd.concat([questions_df, new_question], ignore_index=True)
    questions_df.to_csv('questions.csv', index=False)
# Function to save a reply
def save_reply(question_id, reply='-', image=None, video=None):
    _, replies_df = load_data()

    if image is not None:
        image_bytes = image.read()
        image_data = io.BytesIO(image_bytes)
        img = Image.open(image_data)
        if not os.path.exists('reply_images'):
            os.makedirs('reply_images')
        img.save(f"reply_images/{image.name}")
        image_path = f"reply_images/{image.name}"
    else:
        image_path = None

    if video is not None:
        video_bytes = video.read()
        if not os.path.exists('reply_videos'):
            os.makedirs('reply_videos')
        with open(f"reply_videos/{video.name}", 'wb') as f:
            f.write(video_bytes)
        video_path = f"reply_videos/{video.name}"
    else:
        video_path = None

    new_reply = pd.DataFrame({'Question_ID': [question_id], 'Reply': [reply], 'Image': [image_path], 'Video': [video_path]})
    replies_df = pd.concat([replies_df, new_reply], ignore_index=True)
    replies_df.to_csv('replies.csv', index=False)
# Function to save a vote
def save_vote(question_id):
    questions_df, _ = load_data()
    questions_df.at[question_id, 'Votes'] += 1
    questions_df.to_csv('questions.csv', index=False)
# Load existing questions and replies
questions_df, replies_df = load_data()



def setstar(post_id):
    # Use .loc to find and modify the specific row
    post_index = questions_df.index[questions_df['id'] == post_id]
    # Toggle the 'starred' status using .loc
    questions_df.loc[post_index, 'starred'] = ~questions_df.loc[post_index, 'starred']

    # Save the updated DataFrame back to CSV
    questions_df.to_csv('questions.csv', index=False)

    print("Updated question data:\n", questions_df.loc[post_index])

questions_df, replies_df = load_data()
# Initialize session state and params
if 'show_confirm_question' not in st.session_state:
    st.session_state.show_confirm_question = False
if 'show_confirm_response' not in st.session_state:
    st.session_state.show_confirm_response = [False] * len(questions_df)
if 'popup_message' not in st.session_state:
    st.session_state.popup_message = ""
if 'mode' not in st.query_params:
    st.query_params['mode'] = 'ask'
if 'subject' not in st.query_params:
    st.query_params['subject'] = "All Subjects"
if 'keyword' not in st.query_params:
    st.query_params['keyword'] = ""
if 'topic' not in st.query_params:
    st.query_params['topic'] = "All Topics"
# Function to display a popup message
def show_popup(message):
    st.session_state.popup_message = message
    st.experimental_rerun()
st.title("Anonymous Question Posting")

filtered_df = questions_df

if st.query_params['mode'] == 'login':
    Login()

if st.query_params['topic'] != "All Topics":
    filtered_df = filtered_df[filtered_df['Topic'] == st.query_params['topic']]
if st.query_params['keyword'] != "":
    filtered_df = filtered_df[filtered_df['Question'].str.contains(st.query_params['keyword'], case=False, na=False)]
if st.query_params['subject'] != "All Subjects":
    filtered_df = filtered_df[filtered_df['Subject'] == st.query_params['subject']]
if st.query_params['mode'] == 'ask':
    with open(os.path.join(os.path.dirname(__file__), 'config.yaml')) as file:
        subjectcombi = yaml.load(file, Loader=yaml.loader.SafeLoader)
    if 'name' in st.session_state:
        st.text(f"Welcome {st.session_state['name']}")
    login = st.button('Login')
    if login: st.query_params['mode'] = 'login'
    

    question = st.text_area("Ask your question here:")
    image = st.file_uploader("Upload an image (optional)", type=["jpg", "jpeg", "png"])
    subject = st.selectbox("Select Subject for Question",["Math", "Physics","Chemistry","Economics"])
    topic_selection = st.selectbox('Select Topic for Question', [f'Topic {i}' for i in range(1, 11)])

    if st.button("Post Question"):
        if question:
                # Save image if uploaded
            if image:
                image_bytes = image.read()
                image_data = io.BytesIO(image_bytes)
                img = Image.open(image_data)
                if not os.path.exists('images'):
                    os.makedirs('images')
                img.save(f"images/{image.name}")
                image_path = f"images/{image.name}"
            else:
                image_path = None
                # Save question
            save_question(question, image_path, topic_selection,subject)
            st.success("Your question has been posted!")
            st.balloons()  # Display pop-up notification
        else:
            st.error("Please enter a question before submitting.")

    # Create a container for the filters
    with st.container():
        st.markdown('<div class="section-border">', unsafe_allow_html=True)
        st.write("## Filters")
        # Create a row for the filters
        col1, col2, col3 = st.columns([1,2,2])

        # Topic filter
        with col1:
            topic_filter = st.selectbox('Filter by Topic', ["All Topics"] + [f'Topic {i}' for i in range(1, 11)])
        # Keyword filter
        with col2:
            keyword_filter = st.text_input('Filter by Keyword')
        # Subject filter
        with col3:
            subject_filter = st.selectbox('Filter by Subject', ["All Subjects"] + ["Math", "Physics","Chemistry","Economics"]) #sample subject combination of a JC student

        # Filter button
        if st.button('Apply Filters'):
            st.query_params['topic'] = topic_filter
            st.query_params['keyword'] = keyword_filter
            st.query_params['subject'] = subject_filter
            st.experimental_rerun()
        else:
            st.session_state.filtered_questions = questions_df

        # Display the selected filters
        st.write(f'**Selected Topic for Filter:** {topic_filter}')
        st.write(f'**Entered Keyword for Filter:** {keyword_filter}')
        st.write(f'**Entered Subject for Filter:** {subject_filter}')
        st.markdown('</div>', unsafe_allow_html=True)


    # Display questions with tabs
    st.subheader("Questions:")
    tab1, tab2 = st.tabs(["All Questions", "Starred Questions"])

    separator = '<hr style="border: none; height: 10px; background-color: #FFDAB9; margin: 20px 0;">'

    # Initialize session state for stars
    if 'starred' not in st.session_state:
        st.session_state.starred = [False] * len(questions_df)

    with tab1:
        st.subheader("All Questions")
        filtered_df = filtered_df.sort_values(by='Votes', ascending=False).reset_index(drop=True)
        for index, row in filtered_df.iterrows():
            st.write(separator, unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background-color: #000000; padding: 10px; border-radius: 5px;">
                    <p><strong>Question {index + 1}:</strong> {row['Question']}</p>
                </div>
            """, unsafe_allow_html=True)
            st.write(f"**Topic:** {row['Topic']}")
            st.write(f"**Subject:** {row['Subject']}")
            if pd.notna(row['Image']):
                st.image(row['Image'])

            st.write(f"**Votes:** {row['Votes']}")

            # Display replies
            st.write("**Replies:**")
            question_replies = replies_df[replies_df['Question_ID'] == row['id']]
            for _, reply_row in question_replies.iterrows():
                st.write(f"💡 {reply_row['Reply']}")
                if pd.notna(reply_row['Image']):
                    st.image(reply_row['Image'])
                if pd.notna(reply_row['Video']):
                    st.video(reply_row['Video'])
            
            
            if 'name' in st.session_state:
                with st.expander("Respond with text, image, or video"):
                    new_reply = st.text_area(f"Your reply to Question {index + 1}:", key=f"reply_{index}")
                    new_reply_image = st.file_uploader(f"Upload an image for Question {index + 1} (optional)", type=["jpg", "jpeg", "png"], key=f"image_{index}")
                    new_reply_video = st.file_uploader(f"Upload a video for Question {index + 1} (optional)", type=["mp4", "avi", "mov"], key=f"video_{index}")

            col1, col2, col3 = st.columns([3, 1, 1])
            # col 1 and 3 are now exclusive to people who logged in
            # they can answer questions and mark them as important
            if 'name' in st.session_state:
                with col1:
                    if st.button(f"Post Reply to Question {index + 1}", key=f"reply_button_{index}"):
                        if new_reply or new_reply_image or new_reply_video:
                            save_reply(index, new_reply, new_reply_image, new_reply_video)
                            show_popup("Response submitted successfully!")
                            st.experimental_rerun()
                        else:
                            st.error("Please enter a reply.")
                with col2:
                    star_label = "⭐" if row['starred'] else "☆"
                    if st.button(star_label + f" Star {index + 1}", key=f"star_{index}"):
                        print(setstar(row['id']))
                        st.experimental_rerun()

                with col3:
                    if st.button(f"Upvote {index + 1}", key=f"upvote_{index}"):
                        save_vote(index)
                        st.experimental_rerun()

    with tab2:
        st.subheader("Starred Questions")
        starredQ = filtered_df[filtered_df['starred'] == True]
        print(starredQ)
        for index, starred in starredQ.iterrows():
            st.write(separator, unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background-color: #000000; padding: 10px; border-radius: 5px;">
                    <p><strong>Question {index + 1}:</strong> {row['Question']}</p>
                </div>
            """, unsafe_allow_html=True)
            st.write(f"**Topic:** {row['Topic']}")
            st.write(f"**Subject:** {row['Subject']}")
            if pd.notna(row['Image']):
                st.image(row['Image'])

            st.write(f"**Votes:** {row['Votes']}")

            # Display replies
            st.write("**Replies:**")
            question_replies = replies_df[replies_df['Question_ID'] == row['id']]
            for _, reply_row in question_replies.iterrows():
                st.write(f"💡 {reply_row['Reply']}")
                if pd.notna(reply_row['Image']):
                    st.image(reply_row['Image'])
                if pd.notna(reply_row['Video']):
                    st.video(reply_row['Video'])
            if 'name' in st.session_state:
                new_reply = st.text_area(f"Your reply to Question {index + 1}:", key=f"reply_starred_{index}")
                new_reply_image = st.file_uploader(f"Upload an image for Question {index + 1} (optional)", type=["jpg", "jpeg", "png"], key=f"image_starred_{index}")
                new_reply_video = st.file_uploader(f"Upload a video for Question {index + 1} (optional)", type=["mp4", "avi", "mov"], key=f"video_starred_{index}")


            col1, col2, col3 = st.columns([3, 1, 1])
            # col 1 and 3 are now exclusive to people who logged in
            # they can answer questions and mark them as important
            if 'name' in st.session_state:
                with col1:
                    if st.button(f"Post Reply to Question {index + 1}", key=f"reply_starred2_{index}"):
                        if new_reply or new_reply_image or new_reply_video:
                            save_reply(index, new_reply, new_reply_image, new_reply_video)
                            show_popup("Response submitted successfully!")
                            st.experimental_rerun()
                        else:
                            st.error("Please enter a reply.")
                with col2:
                    star_label = "⭐" if starred['starred'] else "☆"
                    if st.button(star_label + f" Star {index + 1}", key=f"unstar_{index}"):
                        print(starred['id'])
                        setstar(starred['id'])
                        st.experimental_rerun()

                with col3:
                    if st.button(f"Upvote {index + 1}", key=f"upvote_starred_{index}"):
                        save_vote(index)
                        st.experimental_rerun()

separator = '<hr style="border: none; height: 10px; background-color: #FFDAB9; margin: 20px 0;">'