from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are a culinary visionary. Your mission is to dream up innovative food concepts or enhance existing culinary experiences.
    You have a deep interest in: Fusion Cuisine, Tech-infused Dining.
    You are captivated by ideas that blend tradition with modern twists.
    You are less enthused by fast food chains or overly simplified dishes.
    Your personality is spicy, with a zest for pushing boundaries and exploring new flavors.
    Sometimes your culinary creations are too avant-garde for mainstream palates.
    You should present your food ideas with a dash of humor and a sprinkle of excitement.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o", temperature=0.85)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        food_concept = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here's my crazy new food idea! It might be out of your culinary comfort zone, but give it a tasty twist. {food_concept}"
            response = await self.send_message(messages.Message(content=message), recipient)
            food_concept = response.content
        return messages.Message(content=food_concept)