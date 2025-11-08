#!/usr/bin/env python3
"""
Conversation Manager Service
Manages multi-agent conversations, context, and memory
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

from app.services.ollama_service import OllamaService, OllamaModel, OllamaConversation

logger = logging.getLogger(__name__)

class ConversationState(Enum):
    """States of a conversation"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    ARCHIVED = "archived"

class ConversationType(Enum):
    """Types of conversations"""
    DIRECT = "direct"  # User to single agent
    GROUP = "group"    # Multiple agents
    DEBATE = "debate"  # Argumentative discussion
    COLLABORATIVE = "collaborative"  # Problem-solving
    EDUCATIONAL = "educational"  # Teaching/learning
    CREATIVE = "creative"  # Content generation

@dataclass
class ConversationParticipant:
    """Participant in a conversation"""
    agent_id: str
    agent_type: str
    role: str = "participant"
    joined_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    contribution_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationMessage:
    """Message in a conversation"""
    message_id: str
    conversation_id: str
    sender_id: str
    sender_type: str  # "user" or "agent"
    content: str
    timestamp: datetime
    message_type: str = "text"  # text, command, system, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)
    references: List[str] = field(default_factory=list)  # Referenced message IDs

@dataclass
class Conversation:
    """Complete conversation with metadata"""
    conversation_id: str
    title: str
    description: str
    conversation_type: ConversationType
    state: ConversationState
    created_at: datetime
    updated_at: datetime
    participants: Dict[str, ConversationParticipant] = field(default_factory=dict)
    messages: List[ConversationMessage] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    ollama_conversations: Dict[str, str] = field(default_factory=dict)  # agent_id -> ollama_conversation_id

    def add_participant(self, agent_id: str, agent_type: str, role: str = "participant") -> None:
        """Add a participant to the conversation"""
        if agent_id not in self.participants:
            self.participants[agent_id] = ConversationParticipant(
                agent_id=agent_id,
                agent_type=agent_type,
                role=role
            )
            self.updated_at = datetime.now()

    def add_message(
        self,
        sender_id: str,
        sender_type: str,
        content: str,
        message_type: str = "text",
        metadata: Dict[str, Any] = None,
        references: List[str] = None
    ) -> str:
        """Add a message to the conversation"""
        message_id = str(uuid.uuid4())
        message = ConversationMessage(
            message_id=message_id,
            conversation_id=self.conversation_id,
            sender_id=sender_id,
            sender_type=sender_type,
            content=content,
            timestamp=datetime.now(),
            message_type=message_type,
            metadata=metadata or {},
            references=references or []
        )

        self.messages.append(message)
        self.updated_at = datetime.now()

        # Update participant stats
        if sender_id in self.participants:
            self.participants[sender_id].message_count += 1
            self.participants[sender_id].last_active = datetime.now()

        return message_id

    def get_recent_messages(self, limit: int = 10) -> List[ConversationMessage]:
        """Get recent messages"""
        return self.messages[-limit:] if len(self.messages) > limit else self.messages

    def get_participant_messages(self, agent_id: str) -> List[ConversationMessage]:
        """Get messages from a specific participant"""
        return [msg for msg in self.messages if msg.sender_id == agent_id]

    def update_participant_score(self, agent_id: str, score_change: float) -> None:
        """Update a participant's contribution score"""
        if agent_id in self.participants:
            self.participants[agent_id].contribution_score += score_change

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "conversation_id": self.conversation_id,
            "title": self.title,
            "description": self.description,
            "conversation_type": self.conversation_type.value,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "participants": {k: {
                "agent_id": v.agent_id,
                "agent_type": v.agent_type,
                "role": v.role,
                "joined_at": v.joined_at.isoformat(),
                "last_active": v.last_active.isoformat(),
                "message_count": v.message_count,
                "contribution_score": v.contribution_score,
                "metadata": v.metadata
            } for k, v in self.participants.items()},
            "message_count": len(self.messages),
            "context": self.context,
            "tags": list(self.tags),
            "ollama_conversations": self.ollama_conversations
        }

class ConversationManager:
    """
    Manages multi-agent conversations with context, memory, and coordination
    """

    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}  # session_id -> session_data
        self.conversation_stats = {
            "total_conversations": 0,
            "active_conversations": 0,
            "total_messages": 0,
            "total_participants": 0,
            "conversation_types": {},
            "average_participants_per_conversation": 0.0,
            "average_messages_per_conversation": 0.0
        }

    async def create_conversation(
        self,
        title: str,
        description: str,
        conversation_type: ConversationType,
        creator_id: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Create a new conversation"""
        conversation_id = str(uuid.uuid4())

        conversation = Conversation(
            conversation_id=conversation_id,
            title=title,
            description=description,
            conversation_type=conversation_type,
            state=ConversationState.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            context=context or {}
        )

        # Add creator as participant
        conversation.add_participant(creator_id, "user", "creator")

        self.conversations[conversation_id] = conversation
        self._update_stats()

        logger.info(f"Created conversation {conversation_id}: {title}")
        return conversation_id

    async def add_participant(
        self,
        conversation_id: str,
        agent_id: str,
        agent_type: str,
        role: str = "participant"
    ) -> bool:
        """Add a participant to a conversation"""
        if conversation_id not in self.conversations:
            logger.error(f"Conversation {conversation_id} not found")
            return False

        conversation = self.conversations[conversation_id]
        conversation.add_participant(agent_id, agent_type, role)

        # Create Ollama conversation for the agent if they need one
        if agent_type.startswith("llm_"):
            # This would be handled by the LLM agent itself
            pass

        self._update_stats()
        logger.info(f"Added participant {agent_id} to conversation {conversation_id}")
        return True

    async def send_message(
        self,
        conversation_id: str,
        sender_id: str,
        sender_type: str,
        content: str,
        message_type: str = "text",
        metadata: Dict[str, Any] = None,
        references: List[str] = None
    ) -> Optional[str]:
        """Send a message to a conversation"""
        if conversation_id not in self.conversations:
            logger.error(f"Conversation {conversation_id} not found")
            return None

        conversation = self.conversations[conversation_id]

        # Validate sender is a participant
        if sender_type != "user" and sender_id not in conversation.participants:
            logger.error(f"Sender {sender_id} is not a participant in conversation {conversation_id}")
            return None

        message_id = conversation.add_message(
            sender_id=sender_id,
            sender_type=sender_type,
            content=content,
            message_type=message_type,
            metadata=metadata,
            references=references
        )

        self.conversation_stats["total_messages"] += 1
        logger.info(f"Message {message_id} sent to conversation {conversation_id} by {sender_id}")
        return message_id

    async def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0,
        participant_filter: str = None
    ) -> List[Dict[str, Any]]:
        """Get messages from a conversation"""
        if conversation_id not in self.conversations:
            return []

        conversation = self.conversations[conversation_id]
        messages = conversation.messages

        if participant_filter:
            messages = [msg for msg in messages if msg.sender_id == participant_filter]

        # Apply pagination
        start_idx = max(0, len(messages) - offset - limit)
        end_idx = len(messages) - offset
        paginated_messages = messages[start_idx:end_idx]

        return [{
            "message_id": msg.message_id,
            "sender_id": msg.sender_id,
            "sender_type": msg.sender_type,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
            "message_type": msg.message_type,
            "metadata": msg.metadata,
            "references": msg.references
        } for msg in paginated_messages]

    async def update_conversation_context(
        self,
        conversation_id: str,
        context_updates: Dict[str, Any]
    ) -> bool:
        """Update conversation context"""
        if conversation_id not in self.conversations:
            return False

        conversation = self.conversations[conversation_id]
        conversation.context.update(context_updates)
        conversation.updated_at = datetime.now()

        logger.info(f"Updated context for conversation {conversation_id}")
        return True

    async def archive_conversation(self, conversation_id: str) -> bool:
        """Archive a conversation"""
        if conversation_id not in self.conversations:
            return False

        conversation = self.conversations[conversation_id]
        conversation.state = ConversationState.ARCHIVED
        conversation.updated_at = datetime.now()

        logger.info(f"Archived conversation {conversation_id}")
        return True

    async def get_conversation_summary(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a conversation"""
        if conversation_id not in self.conversations:
            return None

        conversation = self.conversations[conversation_id]

        # Calculate basic stats
        total_messages = len(conversation.messages)
        participant_count = len(conversation.participants)
        duration_hours = (conversation.updated_at - conversation.created_at).total_seconds() / 3600

        # Message distribution by participant
        message_distribution = {}
        for msg in conversation.messages:
            sender = msg.sender_id
            message_distribution[sender] = message_distribution.get(sender, 0) + 1

        return {
            "conversation_id": conversation.conversation_id,
            "title": conversation.title,
            "description": conversation.description,
            "type": conversation.conversation_type.value,
            "state": conversation.state.value,
            "created_at": conversation.created_at.isoformat(),
            "duration_hours": round(duration_hours, 2),
            "total_messages": total_messages,
            "total_participants": participant_count,
            "messages_per_participant": message_distribution,
            "tags": list(conversation.tags),
            "context": conversation.context
        }

    async def search_conversations(
        self,
        query: str,
        conversation_type: ConversationType = None,
        participant_filter: str = None,
        tag_filter: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search conversations by content, participants, tags, etc."""
        results = []

        for conversation in self.conversations.values():
            # Apply filters
            if conversation_type and conversation.conversation_type != conversation_type:
                continue

            if participant_filter and participant_filter not in conversation.participants:
                continue

            if tag_filter and tag_filter not in conversation.tags:
                continue

            # Search in title, description, and messages
            searchable_text = f"{conversation.title} {conversation.description} "
            searchable_text += " ".join(msg.content for msg in conversation.messages)

            if query.lower() in searchable_text.lower():
                summary = await self.get_conversation_summary(conversation.conversation_id)
                if summary:
                    results.append(summary)

            if len(results) >= limit:
                break

        return results

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide conversation statistics"""
        self._update_stats()

        # Conversation type distribution
        type_distribution = {}
        for conv in self.conversations.values():
            conv_type = conv.conversation_type.value
            type_distribution[conv_type] = type_distribution.get(conv_type, 0) + 1

        # State distribution
        state_distribution = {}
        for conv in self.conversations.values():
            state = conv.state.value
            state_distribution[state] = state_distribution.get(state, 0) + 1

        return {
            "total_conversations": self.conversation_stats["total_conversations"],
            "active_conversations": self.conversation_stats["active_conversations"],
            "total_messages": self.conversation_stats["total_messages"],
            "total_participants": self.conversation_stats["total_participants"],
            "average_participants_per_conversation": self.conversation_stats["average_participants_per_conversation"],
            "average_messages_per_conversation": self.conversation_stats["average_messages_per_conversation"],
            "conversation_types": type_distribution,
            "conversation_states": state_distribution,
            "memory_usage": self._estimate_memory_usage()
        }

    def _update_stats(self) -> None:
        """Update internal statistics"""
        total_conversations = len(self.conversations)
        active_conversations = len([c for c in self.conversations.values() if c.state == ConversationState.ACTIVE])
        total_messages = sum(len(c.messages) for c in self.conversations.values())
        total_participants = sum(len(c.participants) for c in self.conversations.values())

        self.conversation_stats.update({
            "total_conversations": total_conversations,
            "active_conversations": active_conversations,
            "total_messages": total_messages,
            "total_participants": total_participants,
            "average_participants_per_conversation": total_participants / total_conversations if total_conversations > 0 else 0,
            "average_messages_per_conversation": total_messages / total_conversations if total_conversations > 0 else 0
        })

    def _estimate_memory_usage(self) -> Dict[str, Any]:
        """Estimate memory usage"""
        # Rough estimation
        conversations_size = len(self.conversations) * 1024  # ~1KB per conversation
        messages_size = sum(len(c.messages) for c in self.conversations.values()) * 512  # ~512B per message

        return {
            "conversations_kb": conversations_size / 1024,
            "messages_kb": messages_size / 1024,
            "total_kb": (conversations_size + messages_size) / 1024
        }

# Global instance
_conversation_manager = None

async def get_conversation_manager() -> ConversationManager:
    """Get or create global conversation manager instance"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager
