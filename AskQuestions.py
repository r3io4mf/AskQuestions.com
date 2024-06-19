pip install streamlit-authenticator
# a python file inside pages 
import pandas as pd
from PIL import Image
import io
import os
import streamlit as st
import streamlit_authenticator as stauth
import yaml
import uuid
# main_page

st.set_page_config(page_title = 'Learning Hub!',page_icon = ':school:')
st.sidebar.markdown(" Main Page🎈")
st.title('Hey There! Welcome to Learning Hub! Sign in now and ask your question!')
st.markdown('Forum Page 🖊️')
st.sidebar.markdown('Forum Page 🖊️')
