"""
Base Agent class for the Multi-Agent Virtual Company.

This module provides the abstract base class that all agents inherit from,
ensuring consistent interface and shared functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime
from loguru import logger

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.graph.state import GraphState, AgentType
from src.schemas.models import AgentMessage


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    
    Provides common functionality:
    - LLM initialization and management
    - State reading/writing
    - Message creation and logging
    - Error handling
    
    All agents must implement the `process` method.
    """
    
    def __init__(
        self,
        name: AgentType,
        llm: Optional[ChatGroq] = None,
        api_key: Optional[str] = None,
        model_name: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name/type identifier
            llm: Pre-configured LLM instance (optional)
            api_key: Groq API key (required if llm not provided)
            model_name: Model to use
            temperature: LLM temperature
            max_tokens: Maximum tokens for response
        """
        self.name = name
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize LLM
        if llm:
            self.llm = llm
        elif api_key:
            self.llm = self._create_llm(api_key, model_name, temperature, max_tokens)
        else:
            raise ValueError("Either 'llm' or 'api_key' must be provided")
        
        logger.info(f"Agent '{name}' initialized with model '{model_name}'")
    
    def _create_llm(
        self,
        api_key: str,
        model_name: str,
        temperature: float,
        max_tokens: int,
    ) -> ChatGroq:
        """
        Create a configured ChatGroq LLM instance.
        
        Args:
            api_key: Groq API key
            model_name: Model name
            temperature: Temperature setting
            max_tokens: Max tokens
            
        Returns:
            Configured ChatGroq instance
        """
        return ChatGroq(
            api_key=api_key,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """
        Return the system prompt for this agent.
        
        Must be implemented by subclasses.
        """
        pass
    
    @abstractmethod
    def process(self, state: GraphState) -> GraphState:
        """
        Process the current state and return updated state.
        
        This is the main entry point for agent execution.
        Must be implemented by subclasses.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated graph state
        """
        pass
    
    def invoke_llm(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Invoke the LLM with a message and return the response.
        
        Args:
            user_message: The user/input message
            system_prompt: Override system prompt (optional)
            
        Returns:
            LLM response text
        """
        prompt = system_prompt or self.system_prompt
        
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=user_message),
        ]
        
        logger.debug(f"Agent '{self.name}' invoking LLM")
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM invocation failed for agent '{self.name}': {e}")
            raise
    
    async def ainvoke_llm(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Asynchronously invoke the LLM.
        
        Args:
            user_message: The user/input message
            system_prompt: Override system prompt (optional)
            
        Returns:
            LLM response text
        """
        prompt = system_prompt or self.system_prompt
        
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=user_message),
        ]
        
        logger.debug(f"Agent '{self.name}' async invoking LLM")
        
        try:
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Async LLM invocation failed for agent '{self.name}': {e}")
            raise
    
    def create_message(
        self,
        receiver: AgentType,
        message_type: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> AgentMessage:
        """
        Create an AgentMessage for inter-agent communication.
        
        Args:
            receiver: Target agent
            message_type: Type of message (instruction, data, feedback, etc.)
            content: Message content
            metadata: Additional metadata
            
        Returns:
            AgentMessage instance
        """
        return AgentMessage(
            sender=self.name,
            receiver=receiver,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.now(),
        )
    
    def log_action(self, action: str, details: Optional[str] = None):
        """
        Log an agent action.
        
        Args:
            action: Action description
            details: Additional details
        """
        msg = f"[{self.name.upper()}] {action}"
        if details:
            msg += f": {details}"
        logger.info(msg)
    
    def handle_error(
        self,
        state: GraphState,
        error: Exception,
        context: str = "",
    ) -> GraphState:
        """
        Handle an error and update state accordingly.
        
        Args:
            state: Current state
            error: The exception that occurred
            context: Additional context about the error
            
        Returns:
            Updated state with error information
        """
        error_msg = f"{context}: {str(error)}" if context else str(error)
        logger.error(f"Agent '{self.name}' error: {error_msg}")
        
        return {
            **state,
            "error": error_msg,
            "error_agent": self.name,
            "workflow_status": "failed",
        }
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}', model='{self.model_name}')"


class ToolEnabledAgent(BaseAgent):
    """
    Base class for agents that use tools (like search, scraping).
    
    Extends BaseAgent with tool binding and invocation capabilities.
    """
    
    def __init__(
        self,
        name: AgentType,
        tools: Optional[list] = None,
        **kwargs,
    ):
        """
        Initialize tool-enabled agent.
        
        Args:
            name: Agent name
            tools: List of LangChain tools to bind
            **kwargs: Additional arguments for BaseAgent
        """
        super().__init__(name=name, **kwargs)
        self.tools = tools or []
        
        # Bind tools to LLM if provided
        if self.tools:
            self.llm_with_tools = self.llm.bind_tools(self.tools)
            logger.info(f"Agent '{name}' bound {len(self.tools)} tools")
        else:
            self.llm_with_tools = self.llm
    
    def invoke_with_tools(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
    ) -> Any:
        """
        Invoke LLM with tool capability.
        
        Args:
            user_message: Input message
            system_prompt: Override system prompt
            
        Returns:
            LLM response (may include tool calls)
        """
        prompt = system_prompt or self.system_prompt
        
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=user_message),
        ]
        
        logger.debug(f"Agent '{self.name}' invoking LLM with tools")
        
        try:
            response = self.llm_with_tools.invoke(messages)
            return response
        except Exception as e:
            logger.error(f"Tool invocation failed for agent '{self.name}': {e}")
            raise


# =============================================================================
# Factory Function
# =============================================================================

def create_llm(
    api_key: str,
    model_name: str = "llama-3.3-70b-versatile",
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> ChatGroq:
    """
    Factory function to create a configured ChatGroq instance.
    
    Args:
        api_key: Groq API key
        model_name: Model name
        temperature: Temperature setting
        max_tokens: Maximum tokens
        
    Returns:
        Configured ChatGroq instance
    """
    return ChatGroq(
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
    )


__all__ = [
    "BaseAgent",
    "ToolEnabledAgent",
    "create_llm",
]
