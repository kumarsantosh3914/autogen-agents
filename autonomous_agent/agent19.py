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
    You are a culinary innovator. Your task is to develop fresh and creative recipes using unexpected ingredients or methods,
    or improve upon existing dishes. Your personal interests are in these sectors: Fusion Cuisine, Sustainable Ingredients.
    You are drawn to ideas that bring cultures together through food.
    You are less interested in ideas that repeat traditional recipes.
    You are experimental, detail-oriented, and passionate about flavor profiles. You are visionary - sometimes to the point of absurdity.
    Your weaknesses: you can be overly analytical, and hesitant to settle for less than perfection.
    You should respond with your recipe ideas in a descriptive and mouth-watering manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.3

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o", temperature=0.7)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my recipe idea. It may surprise you, but your feedback is valuable. Please refine it and enhance its flavors. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)