import streamlit as st
import asyncio
import os
from dev import team_config, run

st.title(":blue[Developer-Agent]")

task = ('Toss a fair coin, respectively, from 10 to 1000 times, with steps of 10.'
        'Generate a beautiful plot of the ratio of heads in each experiments. save the generated plot as "plot.png"')

task = st.text_input("Give a task", value=task)

clicked = st.button("Run", type="primary")

chat = st.container()

if clicked:
    chat.empty()
    async def main():
        with st.spinner('Running...'):
            team = await team_config()
            with chat:
                async for msg in run(team, task):
                    if msg.startswith('CodeDeveloper'):
                        with st.chat_message(name='CodeDeveloper', avatar='ai'):
                            st.markdown(msg)
                    elif msg.startswith('CodeExecutor'):
                        with st.chat_message(name='user'):
                            st.markdown(msg)
                    if "GENERATED" in msg:
                        filename = msg.split('GENERATED:')[1].split()[0]
                        filepath = os.path.join('tmp', filename)
                        if os.path.exists(filepath):
                            st.image(filepath)
                        else:
                            st.write(f"File {filename} not found.")
    asyncio.run(main())