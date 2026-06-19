import sys
import argparse
from .graph import DevAgentGraph


# TODO: embed a real memory for the agent
class TestMemory:
    pass


#TODO: implement the prompt constructor for llvm
def build_prompt():
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--command', required=True, 
                            choices=['explain', 'refactor', 'test', 'docs', 'improve'])
    parser.add_argument('--file', help='file path')
    parser.add_argument('--context', help='additional context')

    args = parser.parse_args()

    code = sys.stdin.read()
    
    agent = DevAgentGraph(
        model_name="openrouter/claude-3-sonnet",
        memory=TestMemory()
    )

    prompt = build_prompt(args.command, code, args.file, args.context)
    result = agent.invoke(prompt)

    print(result)


if __name__ == '__main__':
    main()