from agno.agent import Agent
from agno.tools.openweather import OpenWeatherTools
from agno.models.google import Gemini
import os

# Create an agent with OpenWeatherTools
agent = Agent(
    model=Gemini(id="gemini-2.0-flash",api_key=os.getenv("GOOGLE_GEMINI_API_KEY")),
    tools=[
        OpenWeatherTools(
            units="imperial",  # Options: 'standard', 'metric', 'imperial'
            api_key="92cc785a35d051591b2a5f89bdfd730c"
        )
    ],
    markdown=True,
)

# Get current weather for a location
agent.print_response("What's the current weather in Tokyo?", markdown=True)