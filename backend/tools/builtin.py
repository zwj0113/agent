"""
Built-in tools for the AI Agent.
"""
import os
import shutil
from typing import Any

from langchain_core.tools import BaseTool, tool


class CalculatorTool(BaseTool):
    """Calculator tool for evaluating mathematical expressions."""

    name: str = "calculator"
    description: str = "Evaluates mathematical expressions. Input should be a valid Python math expression (e.g., '2 + 2', 'sqrt(16)', 'sin(pi/2)')."

    def _run(self, expression: str) -> str:
        """Synchronously evaluate a math expression."""
        try:
            allowed_functions = {
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'sum': sum, 'pow': pow, 'sqrt': __import__('math').sqrt,
                'sin': __import__('math').sin, 'cos': __import__('math').cos,
                'tan': __import__('math').tan, 'pi': __import__('math').pi,
                'e': __import__('math').e,
            }
            result = eval(expression, {"__builtins__": {}}, allowed_functions)
            return str(result)
        except Exception as exc:
            return f"Error: {exc}"


class WeatherTool(BaseTool):
    """Weather tool - returns mock weather data."""

    name: str = "get_weather"
    description: str = "Get the current weather for a city. Input should be a city name."

    def _run(self, city: str) -> str:
        """Return mock weather data for a city."""
        mock_weather = {
            "beijing": {"temp": 22, "condition": "Sunny", "humidity": 45},
            "shanghai": {"temp": 25, "condition": "Cloudy", "humidity": 60},
            "new york": {"temp": 18, "condition": "Rainy", "humidity": 75},
            "london": {"temp": 15, "condition": "Foggy", "humidity": 80},
            "tokyo": {"temp": 20, "condition": "Windy", "humidity": 55},
        }

        city_lower = city.lower()
        if city_lower in mock_weather:
            data = mock_weather[city_lower]
            return f"Weather in {city}: {data['condition']}, {data['temp']}°C, Humidity: {data['humidity']}%"
        else:
            return f"Weather data for {city} not available. (This is mock data)"


class DiskUsageTool(BaseTool):
    """Get disk usage information for a drive."""

    name: str = "disk_usage"
    description: str = "Get disk usage information. Input should be a drive letter (e.g., 'D:', 'C:') or path."

    def _run(self, path: str = "D:") -> str:
        """Return disk usage information."""
        try:
            # Normalize path
            if not path:
                path = "D:"
            path = path.strip()

            # Get disk usage
            usage = shutil.disk_usage(path)

            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            free_gb = usage.free / (1024**3)
            percent = (usage.used / usage.total) * 100

            return f"Disk {path}:\n- Total: {total_gb:.2f} GB\n- Used: {used_gb:.2f} GB\n- Free: {free_gb:.2f} GB\n- Usage: {percent:.1f}%"
        except Exception as exc:
            return f"Error getting disk usage for {path}: {exc}"
