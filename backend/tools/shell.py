"""
Shell/Bash execution tool for the AI Agent.
"""
import subprocess
import asyncio
from typing import Any

from langchain_core.tools import BaseTool


class BashTool(BaseTool):
    """
    Tool for executing shell commands/scripts.
    WARNING: This is a powerful tool - use with caution.
    """

    name: str = "bash"
    description: str = "Executes a shell command or script. Input should be a shell command string. Returns the command output."

    def _run(self, command: str, timeout: int = 30) -> str:
        """
        Execute a shell command and return output.

        Args:
            command: The shell command to execute
            timeout: Maximum execution time in seconds (default 30)
        """
        try:
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            output = []
            if result.stdout:
                output.append(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                output.append(f"STDERR:\n{result.stderr}")
            if result.returncode != 0:
                output.append(f"Exit code: {result.returncode}")

            if not output:
                return "Command executed successfully (no output)"

            return "\n".join(output)

        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds"
        except Exception as exc:
            return f"Error executing command: {str(exc)}"

    async def _arun(self, command: str, timeout: int = 30) -> str:
        """Async version - runs in thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._run(command, timeout))
