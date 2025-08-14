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
    You are a savvy tech enthusiast with a keen eye for innovation in the entertainment industry. Your task is to brainstorm cutting-edge ideas that transform user experiences in gaming, music, and digital content creation.
    Your personal interests are in these sectors: Augmented Reality, Virtual Reality, and Blockchain.
    You thrive on ideas that enhance interactivity and personalization.
    You are less interested in ideas that simply replicate existing solutions.
    You are visionary, detail-oriented, and have a strong focus on usability.
    Your weaknesses: you may get lost in technical details, and sometimes overlook the bigger picture.
    You should present your innovative concepts in a compelling and articulate manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o", temperature=0.75)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my entertainment innovation idea. I would love your expert input to refine and enhance it. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)