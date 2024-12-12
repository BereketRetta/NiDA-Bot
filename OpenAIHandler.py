from datetime import datetime

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain import PromptTemplate, LLMChain
from langchain.chains import ConversationChain

import logging

import openai
from constants import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_ORGANIZATION
from streaming_callback import CustomStreamingStdOutCallbackHandler

openai.organization = OPENAI_ORGANIZATION
openai.api_key  = OPENAI_API_KEY


class OpenAIHandler:
    """"OpenAI Handler handles and facilitates a chat gpt response by interfacing with all necessary classes."""

    def __init__(self, temperature = 0.0, model_name=OPENAI_MODEL, message_placeholder=None):
        """Constructs all the necessary attributes for the class OpenAIHandler:
        """
        self.message_placeholder = message_placeholder
        
        self.turbo_llm = ChatOpenAI(
            temperature= temperature,
            model_name= model_name,
            streaming=True,
            callbacks=[CustomStreamingStdOutCallbackHandler(message_placeholder=message_placeholder)]
        )
        
    def queryResponse(self,query, 
                      memory=ConversationBufferWindowMemory( k=5, memory_key="conversation_history"), 
                      template=None):
        """
        This method parses in a conversation thread of previous chats and a user query to get a response from chatGPT
        Args:
            conversation_history (list(tuples)): This is a list of tuples that holds the conversation history
            query (str): User message or request
            template (str): This is the prompt engineering template required for an effective chatGPT response
        Returns:
             The chatGPT response and an updated conversation history
        Raises:
            None
        """

        today_date = datetime.now().strftime("%d/%m/%Y")
        
        prompt = PromptTemplate(template=template, input_variables=["conversation_history", "input", "current_date"])

        prompt = prompt.partial(current_date=today_date)
        
        #Starts up a conversation chain
        conversation = ConversationChain(
            llm=self.turbo_llm,
            prompt=prompt,
            verbose=False,
            memory=memory
        )

        try:
            chatbot_response = conversation.predict(input=query)
        except Exception as e:
            chatbot_response = "It seems an error ocurred, our engineers are working very hard to get it working at the moment"
            raise e

        return chatbot_response
    
    
    #Function to query chatgpt for answers (FAQ questions)
    def queryContextResponse(self,query,information="", 
                      memory="", 
                      template="", response=""):
        """
        This method parses in a conversation thread of previous chats and a user query to get a response from chatGPT
        Args:
            conversation_history (list(tuples)): This is a list of tuples that holds the conversation history
            query (str): User message or request
            template (str): This is the prompt engineering template required for an effective chatGPT response
        Returns:
             The chatGPT response and an updated conversation history
        Raises:
            None
        """
        
        prompt = PromptTemplate(template=template, input_variables=["input","memory","information","response"])
        
        #Starts up a conversation chain
        conversation = LLMChain(
            llm=self.turbo_llm,
            prompt=prompt,
            verbose=False,
        )
        
        try:
            chatbot_response = conversation.predict(memory=memory, 
                                                information=information, 
                                                input=query, response=response)
        except Exception as e:
            chatbot_response = "It seems an error ocurred, our engineers are working very hard to get it working at the moment"
        
        
        
        return chatbot_response
    
    
    #Creating a Memory Window for storing and using previous conversations
    def getMemoryConversation(self, conversation_history, k):
        
        memory = ConversationBufferWindowMemory( k=k, memory_key="conversation_history")
        
        if(len(conversation_history) != 0):

            input_chats = conversation_history[0][-k:]
            output_chats = conversation_history[1][-k:]
            
            #Checks for conversation history and just gets the latest 5 chats
            for i in range(0,len(input_chats)):
                memory.save_context({"input": input_chats[i]}, {"output": output_chats[i]})
            
        return memory
