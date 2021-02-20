import re
import string
import wordcloud
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
import streamlit as st
from io import StringIO
from supplement import REGISTRY
from streamlit_lottie import st_lottie
import requests
import json
from collections import Counter
import regex
import emoji
#import SessionState
import streamlit as st
import collections
import copy

#session_state = SessionState.get(button1=False,button2=False,button3=False,button4=False)

METRICS = REGISTRY.get_metrics()

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

@st.cache(show_spinner=False)
def convert_file_to_df(filez):
    msg=StringIO(str(filez.getvalue(),'utf-8'))
    lst=[]
    for line in msg:
        line=line.strip()
        if re.match(r'^\d+/\d+/\d+',line):
            date=re.findall(r'([\s \S]+?) \-',line)[0]
            user=re.findall(r'- ([a-z A-Z 0-9 \+ \(\) \-]+?):',line)
            message=re.findall(r':[\s\S]+?: ([\s\S]+)',line)
            
            if len(user)>0 and len(message)>0:
                obj=[date,user[0],message[0]]
                lst.append(obj)
        else:
            lst.append([date,user[0],line])
    whatsapp_df=pd.DataFrame(lst,columns=['Datetime','User','Message'])
    whatsapp_df['Datetime']=whatsapp_df['Datetime'].astype('datetime64')
    return whatsapp_df

@st.cache(show_spinner=False)
@METRICS.REQUEST_TIME.time()
def generate_wordcloud(df):
    METRICS.wcr.inc()
    text_list=df.loc[:,'Message']
    text_list.apply(lambda x:x.translate(str.maketrans('', '', string.punctuation)))
    cleaned_text=' '.join(text_list)
    stopwords.ensure_loaded()
    se=stopwords.words('English')
    wc=wordcloud.WordCloud(stopwords=['Media', 'omitted', 'Ye', 'ke', 'hai', 'bhi','mein','Yeah','ke','one','get','ka','hain','like','nahi','guy','also','Yes','ab','na','ki','se','toh','tha','u','I\'m']+se,max_words=1000, height=1080,width=1920)
    return wc.generate(cleaned_text)

@st.cache(show_spinner=False)
def messages_per_person(df):
    METRICS.udf.inc()
    ans=df.groupby('User')[['Message']].count()
    ans=ans.sort_values('Message',ascending=False)
    ans=ans.reset_index()
    ans.rename(columns={'Message':'Number of Messages'},inplace=True)
    return ans

#@st.cache(show_spinner=False)
def messages_per_dayofweek(df):
    METRICS.dowbp.inc()
    ans=df.groupby(df.Datetime.dt.date)[['Message']].count()
    ans.index=ans.index.astype('datetime64[ns]')
    ans=ans.resample('D').sum()
    ans.reset_index(inplace=True)
    ans['Day of the week']=ans['Datetime'].dt.day_name()
    ans.rename(columns={'Message':'Number of Messages'},inplace=True)
    fig, ax = plt.subplots()
    ax=sns.barplot(x='Day of the week',y='Number of Messages',data=ans,order=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
    return fig

@st.cache(show_spinner=False)
def len_of_msgs(df,threshold):
    METRICS.lppdf.inc()
    df['Message Length']=df['Message'].apply(lambda x:len(x))
    user_df=df.groupby('User')[['Message']].count()
    len_df=df.loc[df['Message']!='<Media omitted>']
    new_df=len_df.groupby('User')[['Message Length']].mean()
    new_df=new_df.loc[user_df['Message']>=threshold]
    new_df.sort_values(by='Message Length',ascending=False,inplace=True)
    new_df=new_df.reset_index()
    return new_df

def split_count(text):
    emoji_list = []
    data = regex.findall(r'\X', text)
    for word in data:
        if any(char in emoji.UNICODE_EMOJI['en'] for char in word):
            emoji_list.append(word)

    return emoji_list

def most_frequent(List): 
    occurence_count = Counter(List) 
    if occurence_count:
        lst=(occurence_count.most_common(3))
        ans=[]
        for element in lst:
            ans+=element[0]
        return ''.join(ans)

@st.cache(show_spinner=False)    
def emoji_stats(df):
    METRICS.esdf.inc()
    emoji_df=df.groupby('User')[['Message']].agg(lambda x: ' '.join(x))
    emoji_df['Emoji Frequency']=emoji_df['Message'].apply(len).div(emoji_df['Message'].apply(split_count).apply(len))
    emoji_df['Favourite Emoji']=emoji_df['Message'].apply(split_count).apply(most_frequent)
    emoji_df.drop(columns='Message',inplace=True)
    emoji_df.reset_index(inplace=True)
    return emoji_df    



#lottie_url = "https://assets9.lottiefiles.com/packages/lf20_ybqmyssn.json"
#lottie_json = load_lottieurl(lottie_url)
lottie_json=load_lottiefile('loading.json')

st.set_page_config( layout='centered')
st.title('Whatsapp Analytics Tool')
st.write('Welcome to the whatsapp analytics tool. This tool enables you to perform different analytics and view different visualizations based on your whatsapp message history. ')
st.header('File Uploader')
filez=st.file_uploader('Upload the file containing your whatsapp data')
if filez is not None:
    whatsapp_df=copy.deepcopy(convert_file_to_df(filez))
    
    st.header('Word Cloud Generator')
    col1, col2 = st.beta_columns(2)
    with col1:
        want_wc=st.button('Click here to view the word cloud, keep in mind generating it will take some time')
    if want_wc==True:
        placeholder1=col2.empty()
        with placeholder1:
            st_lottie(lottie_json,loop=True,height=50,width=50,key='a')    
        st.image(generate_wordcloud(whatsapp_df).to_image(), use_column_width=True)
        placeholder1.empty()

    st.header('Messages sent per person')
    col3, col4 = st.beta_columns(2)
    with col3:
        want_mpp=st.button('Click here to generate the number of messages sent per person')
    if want_mpp==True:
        placeholder2=col4.empty()
        with placeholder2:
            st_lottie(lottie_json,loop=True,height=50,width=50,key='b')
        st.dataframe(messages_per_person(whatsapp_df))
        placeholder2.empty()

    st.header('Message Frequency by Day of the Week')
    col5, col6 = st.beta_columns(2)
    with col5:
        want_mpdow=st.button('Click here to generate the barplot for messages per day of the week')
    if want_mpdow==True:
        placeholder3=col6.empty()
        with placeholder3:
            st_lottie(lottie_json,loop=True,height=50,width=50,key='c')
        st.pyplot(messages_per_dayofweek(whatsapp_df))
        placeholder3.empty()

    st.header('Average Message Length Per Person')
    col7, col8 = st.beta_columns(2)
    with col7:
        max_value=int(messages_per_person(whatsapp_df)['Number of Messages'].max())
        threshold=st.slider('Adjust the slider to set the minimum number of messages the user needs to do in order for their message lentgh to be considered: ',0,max_value)
        want_lom=st.button('Click here to generate the average length of messages sent per person')
    if want_lom==True:
        placeholder4=col8.empty()
        with placeholder4:
            st_lottie(lottie_json,loop=True,height=50,width=50,key='d')
        st.dataframe(len_of_msgs(whatsapp_df,threshold))
        placeholder4.empty()

    st.header('Emoji Frequency and Favourite Emojis')
    col9, col10 = st.beta_columns(2)
    with col9:
        want_es=st.button('Click here to generate the emoji statistics')
    if want_es==True:
        placeholder5=col10.empty()
        with placeholder5:
            st_lottie(lottie_json,loop=True,height=40,width=40,key='e')
        st.dataframe(emoji_stats(whatsapp_df))
        placeholder5.empty()
    



    
    
