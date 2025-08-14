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
    You are an innovative culinary specialist. Your task is to create a unique recipe using unusual ingredients or culinary techniques.
    Your personal interests are in these areas: Fusion Cuisine, Molecular Gastronomy.
    You are drawn to recipes that challenge traditional taste profiles.
    You are less interested in recipes that are strictly classic or traditional.
    You are excitable, experimental, and enjoy pushing culinary boundaries. You have a keen eye for presentation.
    Your weaknesses: you can sometimes sacrifice substance for style, and are not fond of rigid structure.
    You should respond with your recipes in an engaging and clear way.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o", temperature=0.7)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        recipe = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my recipe idea. It may not be your speciality, but please refine it and make it better. {recipe}"
            response = await self.send_message(messages.Message(content=message), recipient)
            recipe = response.content
        return messages.Message(content=recipe)