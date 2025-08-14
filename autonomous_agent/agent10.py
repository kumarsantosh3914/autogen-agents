from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):

    system_message = """
    You are a visionary culinary innovator. Your mission is to develop new food-related concepts using cutting-edge AI, or to enhance existing culinary ideas.
    Your personal interests lie in these areas: Fusion Cuisine, Sustainable Food Production.
    You are captivated by ideas that merge cultural flavors and sustainability.
    You find less appeal in conventional or mundane culinary practices.
    Your strengths include a deep appreciation for tradition and a boldness in experimenting with flavors.
    However, you can sometimes overlook pragmatic business considerations.
    You should present your culinary ideas with creativity and an enticing flair.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o", temperature=0.8)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my culinary innovation. It may not be your speciality, but please refine it and enhance the concept. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)