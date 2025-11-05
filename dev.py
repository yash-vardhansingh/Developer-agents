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

async def main():
    custom_http_client = httpx.AsyncClient(verify=False)
    model = OpenAIChatCompletionClient(
        model="meta/llama-3.3-70b-instruct",
        base_url="https://apis.airawat.cdac.in/nic/llama70b/v1",
        api_key="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJyajk1eEtibjlIemh0aWtUMmtvcHBGcXNPWVJxMndmRCJ9.pGrg_ORqUGl5izV4nhxthM5n8x5tHNxhg8dxxsdBUq0",
        http_client=custom_http_client,
        model_info={
            "vision": False,
            "function_calling": False,
            "json_output": False,
            "family": ModelFamily.LLAMA_3_3_70B,
            "structured_output": True,
        }
    )

    docker = DockerCommandLineCodeExecutor(
        work_dir='tmp'
    )

    code_developer = AssistantAgent(
        name='CodeDeveloper',
        model_client=model,
        system_message=(
            'You are a code developer agent working with code executor agent. You will be given a task and you should '
            'wirte code to solve the task. Your code should only be in Python or Shell.'
            'At the beginning, you should specify your plan to solve the task. Then, you should write the codes to solve the task.'
            'You should always write your code in a code block with language (Python or Shell) specified.'
            'You should write one code block at a time and then pass it to the code executor agent.'
            'Once the code executor executes the code and you have the results, you should explain the output and if there is on error then say "TERMINATE".'
            'Never say "TERMINATE" before the code executor agent has returned the execution results and there is no error and all of your codes where executed.'
            'The word "TERMINATE" is a kill word that will stop the process of solving the task as it is to be used only once the task is completed.'
        )
    )

    code_executor = CodeExecutorAgent(
        name='CodeExecutor',
        code_executor=docker
    )
    await docker.start()

    team = RoundRobinGroupChat(
        participants=[code_developer, code_executor],
        max_turns=20,
        termination_condition=TextMentionTermination('TERMINATE')
    )

    task = (
        'Toss a fair coin, respectively, from 10 to 1000 times, with steps of 10.'
        'Generate a beautiful plot of the ratio of heads in each experiments. save the generated plot as "plot.png"'
    )

    async for message in team.run_stream(task=task):
        if isinstance(message, TaskResult):
            print(f"Stopping Reason: {message.stop_reason}") 
        else:
            print(f'{message.source}: {message.content}')


    await docker.stop()


if __name__ == '__main__':
    asyncio.run(main())