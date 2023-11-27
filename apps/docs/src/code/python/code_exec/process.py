from os import getenv

from e2b import Sandbox

E2B_API_KEY = getenv("E2B_API_KEY")


def print_out(output):
    print(output.line)


def main():
    # 1. Start the playground sandbox
    sandbox = Sandbox(
        # You can pass your own sandbox template id
        template="base",
        api_key=E2B_API_KEY,
    )

    # 2. Save the LLM-generated code inside the playground
    llm_generated_code = """print("This code was generated by LLM")"""
    sandbox.filesystem.write("/main.py", llm_generated_code)

    # 3. Start the execution of the JavaScript file we saved
    proc = sandbox.process.start(  # $HighlightLine
        cmd="python3 /main.py",  # $HighlightLine
        # 4. Stream stdout, stderr
        on_stdout=print_out,  # $HighlightLine
        on_stderr=print_out,  # $HighlightLine
    )  # $HighlightLine

    # 4. Wait for the process to finish
    proc.wait()

    # 5. Or you can access output after the process has finished
    output = proc.output

    sandbox.close()


main()
