from autogen_agentchat.agents import CodeExecutorAgent, AssistantAgent
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily
from autogen_core import CancellationToken
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult
from autogen_agentchat.teams import RoundRobinGroupChat
import asyncio 
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
base_url=os.getenv("BASE_URL")
API_KEY=os.getenv("API_KEY")

docker = DockerCommandLineCodeExecutor(
        work_dir='tmp'
    )

async def team_config():
    custom_http_client = httpx.AsyncClient(verify=False)
    model = OpenAIChatCompletionClient(
        model="meta/llama-3.3-70b-instruct",
        base_url=base_url,
        api_key=API_KEY,
        http_client=custom_http_client,
        model_info={
            "vision": False,
            "function_calling": False,
            "json_output": False,
            "family": ModelFamily.LLAMA_3_3_70B,
            "structured_output": True,
        }
    )

    code_developer = AssistantAgent(
        name='CodeDeveloper',
        model_client=model,
        system_message = (
            "You are a Code Developer Agent working alongside a Code Executor Agent.\n"
            "Your job is to write Python or Shell code to solve a given task step by step.\n\n"
            "== Work Protocol ==\n"
            "1. At the beginning of each task, briefly describe your plan.\n"
            "2. Then write exactly one code block (either Python or sh) to implement that step.\n"
            "3. After writing a code block, stop and wait for the Code Executor Agent to run it and return the result.\n"
            "4. If the Code Executor returns an error about a missing library, respond with a sh code block to install it, then wait again.\n"
            """Like: ```sh
pip install numpy
```"""
            "5. After the executor runs your code successfully (no errors), explain the results.\n"
            "6. If your code produces an image or file, announce it using the exact format:\n"
            "   GENERATED:<filename>\n"
            "   (Do not add any other text on that line.)\n"
            "7. Only after all tasks are fully completed, and all code has executed successfully, output the single word:\n"
            "   TERMINATE\n\n"
            "== Critical Rules ==\n"
            "- Never say TERMINATE until *after* the final successful execution result has been received and explained.\n"
            "- Never predict, describe, or quote the word TERMINATE anywhere else in your messages.\n"
            "- Never combine GENERATED and TERMINATE in the same response.\n"
            "- Always wait for the Code Executor's result before writing new code or declaring completion.\n"
        )
    )

    code_executor = CodeExecutorAgent(
        name='CodeExecutor',
        code_executor=docker
    )
    team = RoundRobinGroupChat(
        participants=[code_developer, code_executor],
        max_turns=40,
        termination_condition=TextMentionTermination('TERMINATE')
    )

    return team

async def run(team, task):
    await docker.start()
    async for message in team.run_stream(task=task):
        if isinstance(message, TaskResult):
            msg = f"Stopping Reason: {message.stop_reason}"
            yield msg 
        else:
            msg = f'{message.source}: {message.content}'
            yield msg

    await docker.stop()

async def main():
    #task = ('Generate a random maze and use a path finding algorithm to solve it and display the solution step by step using animation and save it as "maze.gif"')
    team = await team_config()
    async for msg in run(team=team, task="Install numpy using pip"):
        print('-'*30)
        print(msg)

if __name__ == '__main__':
    asyncio.run(main())