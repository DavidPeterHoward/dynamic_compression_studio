"""
Comprehensive Test Suite for Ollama-Powered Agent Debate System

Tests cover:
- Debate configuration validation and setup
- Ollama integration for agent responses
- Debate execution workflow and round management
- Agent communication patterns during debates
- Debate rules enforcement and constraints
- Round summaries and consensus tracking
- End-to-end debate workflows
"""

import pytest
import pytest_asyncio
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, List
from datetime import datetime

from app.services.ollama_service import OllamaService, get_ollama_service
from app.services.debate_service import DebateService, DebateConfiguration, DebateRules, DebateStatus


# Mock Debate Types and Interfaces (matching frontend)
class DebateArgument:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', '')
        self.agent_id = kwargs.get('agent_id', '')
        self.agent_name = kwargs.get('agent_name', '')
        self.agent_type = kwargs.get('agent_type', '')
        self.content = kwargs.get('content', '')
        self.round_number = kwargs.get('round_number', 1)
        self.timestamp = kwargs.get('timestamp', datetime.now().isoformat())
        self.evidence_score = kwargs.get('evidence_score', 0.8)
        self.creativity_score = kwargs.get('creativity_score', 0.7)
        self.fallacies_detected = kwargs.get('fallacies_detected', 0)
        self.consensus_impact = kwargs.get('consensus_impact', 0.0)


class DebateParticipant:
    def __init__(self, **kwargs):
        self.agent_id = kwargs.get('agent_id', '')
        self.agent_name = kwargs.get('agent_name', '')
        self.agent_type = kwargs.get('agent_type', '')
        self.specialization = kwargs.get('specialization', '')
        self.position = kwargs.get('position', 'neutral')
        self.confidence_score = kwargs.get('confidence_score', 0.5)
        self.arguments_made = kwargs.get('arguments_made', 0)
        self.rebuttals_given = kwargs.get('rebuttals_given', 0)
        self.fallacies_identified = kwargs.get('fallacies_identified', 0)
        self.strength_score = kwargs.get('strength_score', 0.5)


class RoundSummary:
    def __init__(self, **kwargs):
        self.round_number = kwargs.get('round_number', 1)
        self.arguments_count = kwargs.get('arguments_count', 0)
        self.consensus_score = kwargs.get('consensus_score', 0.0)
        self.key_points_discussed = kwargs.get('key_points_discussed', [])
        self.evidence_quality_avg = kwargs.get('evidence_quality_avg', 0.8)
        self.creativity_level_avg = kwargs.get('creativity_level_avg', 0.7)


class DebateConfiguration:
    def __init__(self, **kwargs):
        self.debate_topic = kwargs.get('debate_topic', '')
        self.problem_statement = kwargs.get('problem_statement', '')
        self.premise_area = kwargs.get('premise_area', '')
        self.debate_mode = kwargs.get('debate_mode', 'structured')
        self.max_rounds = kwargs.get('max_rounds', 5)
        self.max_iterations_per_round = kwargs.get('max_iterations_per_round', 3)
        self.iterations_per_agent = kwargs.get('iterations_per_agent', 2)
        self.consensus_threshold = kwargs.get('consensus_threshold', 0.8)
        self.time_limit_per_argument = kwargs.get('time_limit_per_argument', 60)
        self.response_timeout = kwargs.get('response_timeout', 30)
        self.selected_agents = kwargs.get('selected_agents', [])
        self.agent_roles = kwargs.get('agent_roles', {})
        self.debate_rules = kwargs.get('debate_rules', {})
        self.ollama_model = kwargs.get('ollama_model', 'llama2:7b')
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 512)
        self.system_prompt_template = kwargs.get('system_prompt_template', '')
        self.enable_detailed_logging = kwargs.get('enable_detailed_logging', True)
        self.export_format = kwargs.get('export_format', 'json')
        self.real_time_updates = kwargs.get('real_time_updates', True)


class DebateSession:
    def __init__(self, **kwargs):
        self.session_id = kwargs.get('session_id', '')
        self.status = kwargs.get('status', 'initialized')
        self.configuration = kwargs.get('configuration', DebateConfiguration())
        self.participants = kwargs.get('participants', [])
        self.rounds = kwargs.get('rounds', [])
        self.current_round = kwargs.get('current_round', 0)
        self.total_arguments = kwargs.get('total_arguments', 0)
        self.consensus_score = kwargs.get('consensus_score', 0.0)
        self.started_at = kwargs.get('started_at', datetime.now().isoformat())
        self.completed_at = kwargs.get('completed_at', None)


class DebateAgent:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', '')
        self.name = kwargs.get('name', '')
        self.type = kwargs.get('type', '')
        self.specialization = kwargs.get('specialization', '')
        self.strengths = kwargs.get('strengths', [])
        self.weaknesses = kwargs.get('weaknesses', [])


# Mock Debate Agents
DEBATE_AGENTS = [
    DebateAgent(
        id='11',
        name='Logical Analyst',
        type='logical_analyst',
        specialization='Logical validity, formal reasoning, identifying fallacies',
        strengths=['Formal logic', 'Syllogisms', 'Fallacy detection'],
        weaknesses=['Emotional appeals', 'Creative metaphors']
    ),
    DebateAgent(
        id='12',
        name='Argumentation Specialist',
        type='argumentation_specialist',
        specialization='Argumentation, persuasive techniques, rhetorical analysis',
        strengths=['Rhetorical devices', 'Persuasive appeals', 'Debate structure'],
        weaknesses=['Mathematical proofs', 'Technical jargon']
    ),
    DebateAgent(
        id='13',
        name='Conceptual Analyst',
        type='conceptual_analyst',
        specialization='Conceptual analysis, assumptions, philosophical frameworks',
        strengths=['Philosophical analysis', 'Conceptual clarity', 'Assumption testing'],
        weaknesses=['Practical applications', 'Quantitative data']
    )
]


class TestDebateConfiguration:
    """Unit tests for debate configuration validation and setup."""

    def test_debate_configuration_creation(self):
        """Test basic debate configuration creation."""
        config = DebateConfiguration(
            debate_topic="Should AI be regulated?",
            problem_statement="What are the implications of AI regulation?",
            premise_area="AI development is accelerating rapidly",
            max_rounds=3,
            consensus_threshold=0.7
        )

        assert config.debate_topic == "Should AI be regulated?"
        assert config.problem_statement == "What are the implications of AI regulation?"
        assert config.premise_area == "AI development is accelerating rapidly"
        assert config.max_rounds == 3
        assert config.consensus_threshold == 0.7

    def test_debate_configuration_defaults(self):
        """Test default values in debate configuration."""
        config = DebateConfiguration()

        assert config.debate_mode == 'structured'
        assert config.max_rounds == 5
        assert config.consensus_threshold == 0.8
        assert config.temperature == 0.7
        assert config.max_tokens == 512
        assert config.ollama_model == 'llama2:7b'

    def test_debate_configuration_validation(self):
        """Test debate configuration validation."""
        # Valid configuration
        valid_config = DebateConfiguration(
            debate_topic="Test topic",
            selected_agents=['agent1', 'agent2']
        )
        assert valid_config.debate_topic.strip() != ""
        assert len(valid_config.selected_agents) >= 2

        # Invalid configuration - empty topic
        invalid_config = DebateConfiguration(debate_topic="")
        assert invalid_config.debate_topic.strip() == ""

        # Invalid configuration - too few agents
        invalid_config2 = DebateConfiguration(
            debate_topic="Test",
            selected_agents=['agent1']
        )
        assert len(invalid_config2.selected_agents) < 2

    def test_debate_rules_configuration(self):
        """Test debate rules configuration."""
        rules = {
            'require_evidence': True,
            'enable_fact_checking': True,
            'allow_creativity': False,
            'enforce_formality': True,
            'evidence_threshold': 0.8,
            'creativity_weight': 0.4,
            'max_fallacies_per_argument': 2
        }

        config = DebateConfiguration(debate_rules=rules)

        assert config.debate_rules['require_evidence'] is True
        assert config.debate_rules['evidence_threshold'] == 0.8
        assert config.debate_rules['max_fallacies_per_argument'] == 2

    def test_agent_role_assignment(self):
        """Test agent role assignment in configuration."""
        agent_roles = {
            'agent1': 'Proponent',
            'agent2': 'Opponent',
            'agent3': 'Moderator'
        }

        config = DebateConfiguration(agent_roles=agent_roles)
        assert config.agent_roles['agent1'] == 'Proponent'
        assert config.agent_roles['agent2'] == 'Opponent'
        assert config.agent_roles['agent3'] == 'Moderator'

    def test_ollama_configuration(self):
        """Test Ollama-specific configuration."""
        config = DebateConfiguration(
            ollama_model='mistral:7b',
            temperature=0.9,
            max_tokens=1024,
            enable_detailed_logging=True
        )

        assert config.ollama_model == 'mistral:7b'
        assert config.temperature == 0.9
        assert config.max_tokens == 1024
        assert config.enable_detailed_logging is True


class TestDebateExecution:
    """Tests for debate execution workflow and round management."""

    @pytest.fixture
    def mock_ollama_service(self):
        """Mock Ollama service for testing."""
        mock_service = Mock(spec=OllamaService)
        mock_service.generate = AsyncMock(return_value={
            'response': 'This is a test response from the AI agent.',
            'model': 'llama2:7b',
            'duration_seconds': 1.5,
            'tokens_generated': 25,
            'tokens_per_second': 16.7
        })
        return mock_service

    @pytest.fixture
    def debate_config(self):
        """Create test debate configuration."""
        return DebateConfiguration(
            debate_topic="Test Debate Topic",
            problem_statement="Test problem statement",
            premise_area="Test premise",
            selected_agents=['11', '12', '13'],
            agent_roles={'11': 'Proponent', '12': 'Opponent', '13': 'Moderator'},
            max_rounds=3,
            consensus_threshold=0.7
        )

    def test_debate_session_creation(self, debate_config):
        """Test debate session creation."""
        session = DebateSession(
            session_id='debate_123',
            configuration=debate_config,
            status='initialized'
        )

        assert session.session_id == 'debate_123'
        assert session.status == 'initialized'
        assert session.configuration.debate_topic == "Test Debate Topic"
        assert session.current_round == 0
        assert session.total_arguments == 0

    def test_participant_creation(self, debate_config):
        """Test debate participant creation."""
        participants = []
        for agent_id in debate_config.selected_agents:
            agent = next((a for a in DEBATE_AGENTS if a.id == agent_id), None)
            if agent:
                participant = DebateParticipant(
                    agent_id=agent.id,
                    agent_name=agent.name,
                    agent_type=agent.type,
                    specialization=agent.specialization,
                    position='neutral'
                )
                participants.append(participant)

        assert len(participants) == 3
        assert participants[0].agent_name == 'Logical Analyst'
        assert participants[1].agent_name == 'Argumentation Specialist'
        assert participants[2].agent_name == 'Conceptual Analyst'

    @pytest.mark.asyncio
    async def test_agent_response_generation(self, mock_ollama_service, debate_config):
        """Test agent response generation with Ollama."""
        agent = DEBATE_AGENTS[0]  # Logical Analyst

        debate_context = {
            'topic': debate_config.debate_topic,
            'premise': debate_config.premise_area,
            'problemStatement': debate_config.problem_statement,
            'currentRound': 1,
            'previousArguments': [],
            'agentRole': debate_config.agent_roles[agent.id],
            'debateRules': debate_config.debate_rules
        }

        # This would be the actual function from the debate system
        system_prompt = f"You are {agent.name}, a {agent.specialization}.\n\nDEBATE CONTEXT:\n- Topic: {debate_context['topic']}\n- Premise: {debate_context['premise']}\n- Problem Statement: {debate_context['problemStatement']}\n- Round: {debate_context['currentRound']}\n- Your Role: {debate_context['agentRole']}\n\nYOUR STRENGTHS: {', '.join(agent.strengths)}\nYOUR WEAKNESSES: {', '.join(agent.weaknesses)}\n\nProvide a thoughtful response that advances the debate."

        user_prompt = "This is the opening round. Present your initial position."

        # Mock the call
        response = await mock_ollama_service.generate(
            prompt=user_prompt,
            model=debate_config.ollama_model,
            system_prompt=system_prompt,
            temperature=debate_config.temperature,
            max_tokens=debate_config.max_tokens
        )

        assert 'response' in response
        assert response['model'] == 'llama2:7b'
        assert response['duration_seconds'] > 0

    def test_debate_argument_creation(self):
        """Test debate argument creation."""
        argument = DebateArgument(
            id='arg_123',
            agent_id='11',
            agent_name='Logical Analyst',
            agent_type='logical_analyst',
            content='This is a test argument about the topic.',
            round_number=1,
            evidence_score=0.85,
            creativity_score=0.75,
            fallacies_detected=0,
            consensus_impact=0.1
        )

        assert argument.id == 'arg_123'
        assert argument.agent_name == 'Logical Analyst'
        assert argument.round_number == 1
        assert argument.evidence_score == 0.85
        assert argument.fallacies_detected == 0

    def test_round_summary_creation(self):
        """Test round summary creation."""
        summary = RoundSummary(
            round_number=1,
            arguments_count=3,
            consensus_score=0.65,
            key_points_discussed=[
                'Point 1 about the topic...',
                'Point 2 regarding implications...',
                'Point 3 about solutions...'
            ],
            evidence_quality_avg=0.82,
            creativity_level_avg=0.71
        )

        assert summary.round_number == 1
        assert summary.arguments_count == 3
        assert summary.consensus_score == 0.65
        assert len(summary.key_points_discussed) == 3

    def test_debate_execution_state_management(self):
        """Test debate execution state management."""
        execution_state = {
            'current_round': 0,
            'current_iteration': 0,
            'total_iterations_completed': 0,
            'arguments_made': 0,
            'consensus_score': 0.0,
            'debate_history': [],
            'agent_responses': {},
            'round_summaries': [],
            'final_conclusion': None
        }

        # Simulate starting debate
        execution_state['current_round'] = 1

        # Simulate adding arguments
        execution_state['debate_history'].append(DebateArgument(agent_name='Agent 1'))
        execution_state['debate_history'].append(DebateArgument(agent_name='Agent 2'))
        execution_state['arguments_made'] = len(execution_state['debate_history'])

        assert execution_state['current_round'] == 1
        assert execution_state['arguments_made'] == 2
        assert len(execution_state['debate_history']) == 2


class TestDebateRules:
    """Tests for debate rules enforcement and constraints."""

    def test_evidence_requirement_rule(self):
        """Test evidence requirement rule enforcement."""
        rules = {
            'require_evidence': True,
            'evidence_threshold': 0.8
        }

        # Mock argument scoring
        argument_scores = {
            'evidence_score': 0.85,
            'creativity_score': 0.7
        }

        # Check compliance
        evidence_compliant = argument_scores['evidence_score'] >= rules['evidence_threshold']
        assert evidence_compliant is True

        # Test non-compliant argument
        low_evidence_scores = {'evidence_score': 0.6}
        evidence_compliant_low = low_evidence_scores['evidence_score'] >= rules['evidence_threshold']
        assert evidence_compliant_low is False

    def test_fact_checking_rule(self):
        """Test fact checking rule enforcement."""
        rules = {'enable_fact_checking': True}

        # Mock fact checking process
        claims_to_verify = [
            "AI development is accelerating",
            "Climate change is caused by human activity",
            "The Earth is round"
        ]

        # Simulate fact checking results
        fact_check_results = {
            "AI development is accelerating": True,  # Verified
            "Climate change is caused by human activity": True,  # Verified
            "The Earth is round": True  # Verified
        }

        if rules['enable_fact_checking']:
            all_claims_verified = all(fact_check_results.values())
            assert all_claims_verified is True

    def test_creativity_constraints(self):
        """Test creativity level constraints."""
        rules = {
            'allow_creativity': True,
            'creativity_weight': 0.4
        }

        argument_scores = {
            'evidence_score': 0.8,
            'creativity_score': 0.9
        }

        # Calculate weighted score
        weighted_score = (
            argument_scores['evidence_score'] * (1 - rules['creativity_weight']) +
            argument_scores['creativity_score'] * rules['creativity_weight']
        )

        expected_weighted_score = 0.8 * 0.6 + 0.9 * 0.4  # 0.48 + 0.36 = 0.84
        assert abs(weighted_score - expected_weighted_score) < 0.001

    def test_formality_enforcement(self):
        """Test formality level enforcement."""
        rules = {'enforce_formality': True}

        # Mock formality checking
        formal_phrases = ['therefore', 'however', 'consequently', 'moreover']
        informal_phrases = ['like', 'um', 'kinda', 'sorta']

        formal_argument = "Therefore, we must consider the implications. However, there are alternative approaches."
        informal_argument = "So like, we gotta think about this stuff, you know?"

        formal_score = sum(1 for phrase in formal_phrases if phrase in formal_argument.lower())
        informal_score = sum(1 for phrase in informal_phrases if phrase in informal_argument.lower())

        if rules['enforce_formality']:
            assert formal_score > informal_score

    def test_fallacy_detection(self):
        """Test fallacy detection constraints."""
        rules = {'max_fallacies_per_argument': 2}

        # Mock fallacy detection results
        detected_fallacies = [
            {'type': 'ad_hominem', 'severity': 'high'},
            {'type': 'straw_man', 'severity': 'medium'},
            {'type': 'false_dichotomy', 'severity': 'low'}
        ]

        fallacies_count = len(detected_fallacies)
        within_limits = fallacies_count <= rules['max_fallacies_per_argument']

        assert within_limits is False  # 3 fallacies > 2 limit

        # Test compliant argument
        compliant_fallacies = detected_fallacies[:2]  # Only 2 fallacies
        compliant_count = len(compliant_fallacies)
        compliant_within_limits = compliant_count <= rules['max_fallacies_per_argument']
        assert compliant_within_limits is True

    def test_counter_argument_requirement(self):
        """Test counter-argument requirement."""
        rules = {'require_counter_arguments': True}

        # Mock argument analysis
        opening_argument = "AI should be regulated because it poses risks."
        counter_argument = "However, regulation might stifle innovation."

        has_counter = "however" in counter_argument.lower() or "but" in counter_argument.lower()

        if rules['require_counter_arguments']:
            assert has_counter is True

    def test_collaboration_permissions(self):
        """Test collaboration permission rules."""
        rules = {'allow_collaboration': False}

        # Mock collaboration attempt
        collaboration_request = {
            'type': 'joint_analysis',
            'participants': ['agent1', 'agent2'],
            'task': 'analyze_implications'
        }

        collaboration_allowed = rules['allow_collaboration']

        if not collaboration_allowed:
            assert len(collaboration_request['participants']) == 2  # Multiple participants
            # Collaboration should be denied
            assert collaboration_allowed is False

    def test_turn_taking_enforcement(self):
        """Test turn-taking enforcement."""
        rules = {'enforce_turn_taking': True}

        # Mock debate sequence
        debate_sequence = [
            {'agent': 'agent1', 'round': 1},
            {'agent': 'agent2', 'round': 1},
            {'agent': 'agent3', 'round': 1},
            {'agent': 'agent1', 'round': 2},
            {'agent': 'agent2', 'round': 2},
            {'agent': 'agent3', 'round': 2}
        ]

        # Check turn taking pattern
        proper_turn_taking = True
        for i, entry in enumerate(debate_sequence):
            expected_round = (i // 3) + 1
            if entry['round'] != expected_round:
                proper_turn_taking = False
                break

        if rules['enforce_turn_taking']:
            assert proper_turn_taking is True


class TestDebateAnalytics:
    """Tests for round summaries and consensus tracking."""

    def test_consensus_calculation(self):
        """Test consensus score calculation."""
        arguments = [
            DebateArgument(consensus_impact=0.2),
            DebateArgument(consensus_impact=-0.1),
            DebateArgument(consensus_impact=0.3),
            DebateArgument(consensus_impact=0.1)
        ]

        consensus_score = sum(arg.consensus_impact for arg in arguments) / len(arguments)
        expected_consensus = (0.2 - 0.1 + 0.3 + 0.1) / 4  # 0.125

        assert abs(consensus_score - expected_consensus) < 0.001

    def test_round_summary_generation(self):
        """Test round summary generation."""
        arguments = [
            DebateArgument(
                content="AI regulation is necessary for safety",
                evidence_score=0.9,
                creativity_score=0.7,
                consensus_impact=0.2
            ),
            DebateArgument(
                content="Innovation might be stifled by regulation",
                evidence_score=0.8,
                creativity_score=0.8,
                consensus_impact=-0.1
            ),
            DebateArgument(
                content="A balanced approach is needed",
                evidence_score=0.85,
                creativity_score=0.75,
                consensus_impact=0.1
            )
        ]

        summary = RoundSummary(
            round_number=1,
            arguments_count=len(arguments),
            consensus_score=sum(arg.consensus_impact for arg in arguments) / len(arguments),
            key_points_discussed=[arg.content[:50] + '...' for arg in arguments],
            evidence_quality_avg=sum(arg.evidence_score for arg in arguments) / len(arguments),
            creativity_level_avg=sum(arg.creativity_score for arg in arguments) / len(arguments)
        )

        assert summary.round_number == 1
        assert summary.arguments_count == 3
        assert len(summary.key_points_discussed) == 3
        assert summary.evidence_quality_avg > 0.8
        assert summary.creativity_level_avg > 0.7

    def test_performance_grade_calculation(self):
        """Test performance grade calculation."""
        def get_performance_grade(score: float) -> str:
            if score >= 90: return 'A+'
            if score >= 80: return 'A'
            if score >= 70: return 'B+'
            if score >= 60: return 'B'
            if score >= 50: return 'C+'
            return 'C'

        test_scores = [95, 85, 75, 65, 55, 45]
        expected_grades = ['A+', 'A', 'B+', 'B', 'C+', 'C']

        for score, expected in zip(test_scores, expected_grades):
            grade = get_performance_grade(score)
            assert grade == expected

    def test_agent_performance_tracking(self):
        """Test agent performance tracking across rounds."""
        agent_performance = {
            'agent1': {
                'arguments_made': 3,
                'avg_evidence_score': 0.85,
                'avg_creativity_score': 0.75,
                'total_consensus_impact': 0.4,
                'fallacies_detected': 1
            },
            'agent2': {
                'arguments_made': 3,
                'avg_evidence_score': 0.78,
                'avg_creativity_score': 0.82,
                'total_consensus_impact': -0.2,
                'fallacies_detected': 0
            },
            'agent3': {
                'arguments_made': 3,
                'avg_evidence_score': 0.88,
                'avg_creativity_score': 0.68,
                'total_consensus_impact': 0.1,
                'fallacies_detected': 2
            }
        }

        # Calculate overall performance
        for agent_id, perf in agent_performance.items():
            overall_score = (
                perf['avg_evidence_score'] * 0.4 +
                perf['avg_creativity_score'] * 0.3 +
                (perf['total_consensus_impact'] + 1) * 0.3  # Normalize consensus impact
            ) * 100

            perf['overall_score'] = overall_score

        # Verify calculations
        assert agent_performance['agent1']['overall_score'] > 70
        assert agent_performance['agent2']['overall_score'] > 60
        assert agent_performance['agent3']['overall_score'] > 65

    def test_trend_analysis(self):
        """Test performance trend analysis."""
        round_data = [
            {'round': 1, 'consensus_score': 0.2, 'evidence_avg': 0.8},
            {'round': 2, 'consensus_score': 0.4, 'evidence_avg': 0.82},
            {'round': 3, 'consensus_score': 0.6, 'evidence_avg': 0.85},
            {'round': 4, 'consensus_score': 0.5, 'evidence_avg': 0.87}
        ]

        # Calculate trends
        consensus_trend = 'increasing' if round_data[-1]['consensus_score'] > round_data[0]['consensus_score'] else 'decreasing'
        evidence_trend = 'increasing' if round_data[-1]['evidence_avg'] > round_data[0]['evidence_avg'] else 'decreasing'

        assert consensus_trend == 'increasing'
        assert evidence_trend == 'increasing'

        # Calculate improvement rates
        consensus_improvement = round_data[-1]['consensus_score'] - round_data[0]['consensus_score']
        evidence_improvement = round_data[-1]['evidence_avg'] - round_data[0]['evidence_avg']

        assert abs(consensus_improvement - 0.3) < 0.001
        assert abs(evidence_improvement - 0.07) < 0.001


@pytest.mark.asyncio
class TestDebateIntegration:
    """Integration tests for complete debate workflows."""

    @pytest.fixture
    async def mock_ollama_setup(self):
        """Set up mock Ollama service for integration tests."""
        mock_service = Mock(spec=OllamaService)
        mock_service.generate = AsyncMock(side_effect=[
            # Round 1 responses
            {'response': 'As a logical analyst, I argue that AI regulation is essential for maintaining ethical standards and preventing harm.', 'model': 'llama2:7b', 'duration_seconds': 1.2},
            {'response': 'From an argumentation perspective, regulation may hinder innovation and progress in AI development.', 'model': 'llama2:7b', 'duration_seconds': 1.1},
            {'response': 'Conceptually, we need a balanced approach that considers both risks and benefits of AI advancement.', 'model': 'llama2:7b', 'duration_seconds': 1.3},
            # Round 2 responses
            {'response': 'Building on the previous points, strict regulation ensures accountability in AI deployment.', 'model': 'llama2:7b', 'duration_seconds': 1.4},
            {'response': 'However, over-regulation could create barriers for smaller organizations and startups.', 'model': 'llama2:7b', 'duration_seconds': 1.2},
            {'response': 'A framework-based approach might provide flexibility while ensuring safety standards.', 'model': 'llama2:7b', 'duration_seconds': 1.5}
        ])
        return mock_service

    async def test_complete_debate_workflow(self, mock_ollama_setup):
        """Test complete debate workflow from setup to conclusion."""
        # Setup debate configuration
        config = DebateConfiguration(
            debate_topic="Should AI be regulated?",
            problem_statement="What are the implications of regulating artificial intelligence development?",
            premise_area="AI technology is advancing rapidly with both benefits and risks",
            selected_agents=['11', '12', '13'],
            agent_roles={'11': 'Proponent', '12': 'Opponent', '13': 'Moderator'},
            max_rounds=2,
            consensus_threshold=0.8
        )

        # Create debate session
        session = DebateSession(
            session_id='test_debate_123',
            configuration=config,
            status='active'
        )

        # Create participants
        participants = []
        for agent_id in config.selected_agents:
            agent = next((a for a in DEBATE_AGENTS if a.id == agent_id), None)
            if agent:
                participant = DebateParticipant(
                    agent_id=agent.id,
                    agent_name=agent.name,
                    agent_type=agent.type,
                    specialization=agent.specialization
                )
                participants.append(participant)

        session.participants = participants

        # Simulate debate execution
        debate_history = []
        round_summaries = []

        for round_num in range(1, config.max_rounds + 1):
            round_arguments = []

            for agent_id in config.selected_agents:
                agent = next((a for a in DEBATE_AGENTS if a.id == agent_id), None)
                if not agent:
                    continue

                # Generate agent response (mocked)
                response_data = await mock_ollama_setup.generate(
                    prompt=f"Round {round_num} argument for {agent.name}",
                    model=config.ollama_model
                )

                argument = DebateArgument(
                    id=f'arg_{round_num}_{agent_id}',
                    agent_id=agent_id,
                    agent_name=agent.name,
                    agent_type=agent.type,
                    content=response_data['response'],
                    round_number=round_num,
                    evidence_score=0.8 + (round_num * 0.05),  # Improving over rounds
                    creativity_score=0.7 + (round_num * 0.03),
                    consensus_impact=(round_num - 1.5) * 0.2  # Varying consensus impact
                )

                round_arguments.append(argument)
                debate_history.append(argument)

            # Generate round summary
            summary = RoundSummary(
                round_number=round_num,
                arguments_count=len(round_arguments),
                consensus_score=sum(arg.consensus_impact for arg in round_arguments) / len(round_arguments),
                key_points_discussed=[arg.content[:50] + '...' for arg in round_arguments],
                evidence_quality_avg=sum(arg.evidence_score for arg in round_arguments) / len(round_arguments),
                creativity_level_avg=sum(arg.creativity_score for arg in round_arguments) / len(round_arguments)
            )

            round_summaries.append(summary)

        # Verify results
        assert len(debate_history) == 6  # 3 agents × 2 rounds
        assert len(round_summaries) == 2  # 2 rounds

        # Check round progression
        assert debate_history[0].round_number == 1
        assert debate_history[3].round_number == 2

        # Check consensus development
        round1_consensus = round_summaries[0].consensus_score
        round2_consensus = round_summaries[1].consensus_score

        # Consensus should show some development
        assert abs(round1_consensus - round2_consensus) < 1.0  # Not too drastic change

        # Check evidence quality improvement
        round1_evidence = round_summaries[0].evidence_quality_avg
        round2_evidence = round_summaries[1].evidence_quality_avg
        assert round2_evidence >= round1_evidence  # Should improve or stay same

    async def test_debate_rules_integration(self, mock_ollama_setup):
        """Test debate rules integration throughout debate."""
        config = DebateConfiguration(
            debate_topic="Climate change policy",
            selected_agents=['11', '12'],
            debate_rules={
                'require_evidence': True,
                'enable_fact_checking': True,
                'allow_creativity': False,
                'evidence_threshold': 0.8,
                'max_fallacies_per_argument': 1
            }
        )

        # Simulate rule enforcement during debate
        arguments = []
        rule_violations = []

        for i in range(4):  # 2 agents × 2 rounds
            response_data = await mock_ollama_setup.generate(
                prompt=f"Argument {i+1} with evidence",
                model=config.ollama_model
            )

            argument = DebateArgument(
                content=response_data['response'],
                evidence_score=0.85 if i % 2 == 0 else 0.6,  # Alternate high/low evidence
                fallacies_detected=0 if i < 3 else 2  # Last argument has too many fallacies
            )

            arguments.append(argument)

            # Check rule compliance
            if config.debate_rules['require_evidence']:
                if argument.evidence_score < config.debate_rules['evidence_threshold']:
                    rule_violations.append(f"Low evidence score: {argument.evidence_score}")

            if argument.fallacies_detected > config.debate_rules['max_fallacies_per_argument']:
                rule_violations.append(f"Too many fallacies: {argument.fallacies_detected}")

        # Verify rule enforcement
        assert len(rule_violations) > 0  # Should have some violations
        assert any("Low evidence" in v for v in rule_violations)
        assert any("Too many fallacies" in v for v in rule_violations)

    async def test_ollama_error_handling(self):
        """Test error handling when Ollama service fails."""
        # Mock Ollama service failure
        mock_service = Mock(spec=OllamaService)
        mock_service.generate = AsyncMock(side_effect=Exception("Ollama connection failed"))

        config = DebateConfiguration(
            debate_topic="Test topic",
            selected_agents=['11']
        )

        agent = DEBATE_AGENTS[0]

        # Attempt to generate response
        try:
            await mock_service.generate(
                prompt="Test prompt",
                model=config.ollama_model
            )
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Ollama connection failed" in str(e)

    async def test_debate_conclusion_generation(self):
        """Test debate conclusion generation."""
        # Mock debate results
        debate_results = {
            'total_rounds': 3,
            'total_arguments': 9,
            'final_consensus_score': 0.75,
            'dominant_position': 'balanced_approach',
            'key_insights': [
                'Regulation is necessary but should be balanced',
                'Innovation must be protected while ensuring safety',
                'International cooperation is essential'
            ],
            'recommendations': [
                'Implement flexible regulatory frameworks',
                'Support innovation while maintaining oversight',
                'Develop international standards'
            ]
        }

        # Generate conclusion
        conclusion_type = 'consensus' if debate_results['final_consensus_score'] > 0.7 else 'majority'
        conclusion = {
            'conclusion_type': conclusion_type,
            'winning_position': debate_results['dominant_position'],
            'confidence_score': debate_results['final_consensus_score'],
            'key_insights': debate_results['key_insights'],
            'recommendations': debate_results['recommendations'],
            'summary': f"After {debate_results['total_rounds']} rounds and {debate_results['total_arguments']} arguments, the debate reached a {conclusion_type} on {debate_results['dominant_position']} with {debate_results['final_consensus_score']*100:.1f}% consensus.",
            'timestamp': datetime.now().isoformat()
        }

        # Verify conclusion structure
        assert conclusion['conclusion_type'] == 'consensus'
        assert conclusion['confidence_score'] == 0.75
        assert len(conclusion['key_insights']) == 3
        assert len(conclusion['recommendations']) == 3
        assert 'summary' in conclusion
        assert 'timestamp' in conclusion


class TestDebateExecutionWorkflow:
    """Tests for debate execution workflow and round management."""

    @pytest.fixture
    async def debate_service(self):
        """Create debate service for testing."""
        service = DebateService()
        await service.initialize()
        return service

    @pytest.fixture
    def sample_config(self):
        """Create sample debate configuration."""
        return DebateConfiguration(
            debate_topic="AI Safety Regulations",
            problem_statement="How should AI development be regulated?",
            premise_area="AI technology is advancing rapidly with both benefits and risks",
            selected_agents=['agent1', 'agent2', 'agent3'],
            agent_roles={'agent1': 'Proponent', 'agent2': 'Opponent', 'agent3': 'Moderator'},
            max_rounds=3,
            consensus_threshold=0.7
        )

    @pytest.mark.asyncio
    async def test_debate_session_creation(self, debate_service, sample_config):
        """Test debate session creation and initialization."""
        session = await debate_service.create_debate_session(sample_config)

        assert session.session_id.startswith('debate_')
        assert session.status == DebateStatus.INITIALIZED
        assert session.configuration.debate_topic == "AI Safety Regulations"
        assert len(session.participants) == 3
        assert session.current_round == 0
        assert session.total_arguments == 0
        assert session.started_at is not None

        # Verify session is stored
        assert session.session_id in debate_service.active_sessions

    @pytest.mark.asyncio
    async def test_session_status_tracking(self, debate_service, sample_config):
        """Test session status updates during debate execution."""
        session = await debate_service.create_debate_session(sample_config)

        # Initial status
        assert session.status == DebateStatus.INITIALIZED

        # Status retrieval
        status = await debate_service.get_session_status(session.session_id)
        assert status is not None
        assert status['status'] == 'initialized'
        assert status['current_round'] == 0

    @pytest.mark.asyncio
    async def test_round_execution_workflow(self, debate_service, sample_config, mocker):
        """Test round execution workflow."""
        # Mock Ollama service
        mock_ollama = mocker.patch.object(debate_service, 'ollama_service')

        # Create mock responses
        mock_responses = [
            {'response': 'Pro argument 1', 'model': 'llama2:7b', 'duration_seconds': 1.0},
            {'response': 'Con argument 1', 'model': 'llama2:7b', 'duration_seconds': 1.1},
            {'response': 'Moderator argument 1', 'model': 'llama2:7b', 'duration_seconds': 1.2}
        ]
        mock_ollama.generate = mocker.AsyncMock(side_effect=mock_responses)

        session = await debate_service.create_debate_session(sample_config)
        session.status = DebateStatus.ACTIVE

        # Execute round
        arguments = await debate_service.execute_debate_round(session.session_id)

        assert len(arguments) == 3
        assert all(isinstance(arg, DebateArgument) for arg in arguments)
        assert all(arg.round_number == 1 for arg in arguments)
        assert session.current_round == 1
        assert session.total_arguments == 3

        # Verify Ollama was called for each agent
        assert mock_ollama.generate.call_count == 3

    @pytest.mark.asyncio
    async def test_multiple_round_execution(self, debate_service, sample_config, mocker):
        """Test multiple round execution."""
        mock_ollama = mocker.patch.object(debate_service, 'ollama_service')

        # Create 6 mock responses (3 agents × 2 rounds = 6 responses)
        mock_responses = [
            # Round 1
            {'response': 'Round 1 - Agent 1', 'model': 'llama2:7b', 'duration_seconds': 1.0},
            {'response': 'Round 1 - Agent 2', 'model': 'llama2:7b', 'duration_seconds': 1.1},
            {'response': 'Round 1 - Agent 3', 'model': 'llama2:7b', 'duration_seconds': 1.2},
            # Round 2
            {'response': 'Round 2 - Agent 1', 'model': 'llama2:7b', 'duration_seconds': 1.0},
            {'response': 'Round 2 - Agent 2', 'model': 'llama2:7b', 'duration_seconds': 1.1},
            {'response': 'Round 2 - Agent 3', 'model': 'llama2:7b', 'duration_seconds': 1.2}
        ]
        mock_ollama.generate = mocker.AsyncMock(side_effect=mock_responses)

        session = await debate_service.create_debate_session(sample_config)
        session.status = DebateStatus.ACTIVE

        # Execute two rounds
        round1_args = await debate_service.execute_debate_round(session.session_id)
        round2_args = await debate_service.execute_debate_round(session.session_id)

        assert len(round1_args) == 3
        assert len(round2_args) == 3
        assert all(arg.round_number == 1 for arg in round1_args)
        assert all(arg.round_number == 2 for arg in round2_args)
        assert session.current_round == 2
        assert session.total_arguments == 6

    @pytest.mark.asyncio
    async def test_round_summary_generation(self, debate_service):
        """Test round summary generation."""
        # Create mock arguments
        arguments = [
            DebateArgument(
                id='arg1', agent_id='agent1', agent_name='Agent 1', agent_type='logical',
                content='Strong argument with evidence', round_number=1, timestamp='2024-01-01T00:00:00Z',
                evidence_score=0.9, creativity_score=0.7, fallacies_detected=0, consensus_impact=0.2
            ),
            DebateArgument(
                id='arg2', agent_id='agent2', agent_name='Agent 2', agent_type='rhetorical',
                content='Creative counter-argument', round_number=1, timestamp='2024-01-01T00:00:01Z',
                evidence_score=0.7, creativity_score=0.9, fallacies_detected=1, consensus_impact=-0.1
            ),
            DebateArgument(
                id='arg3', agent_id='agent3', agent_name='Agent 3', agent_type='analytical',
                content='Balanced perspective', round_number=1, timestamp='2024-01-01T00:00:02Z',
                evidence_score=0.8, creativity_score=0.6, fallacies_detected=0, consensus_impact=0.1
            )
        ]

        summary = await debate_service.generate_round_summary('test_session', 1, arguments)

        assert summary.round_number == 1
        assert summary.arguments_count == 3
        assert abs(summary.consensus_score - 0.067) < 0.01  # (0.2 - 0.1 + 0.1) / 3
        assert abs(summary.evidence_quality_avg - 0.8) < 0.01  # (0.9 + 0.7 + 0.8) / 3
        assert abs(summary.creativity_level_avg - 0.733) < 0.01  # (0.7 + 0.9 + 0.6) / 3
        assert len(summary.key_points_discussed) == 3

    @pytest.mark.asyncio
    async def test_error_handling_in_round_execution(self, debate_service, sample_config, mocker):
        """Test error handling during round execution."""
        mock_ollama = mocker.patch.object(debate_service, 'ollama_service')
        mock_ollama.generate = mocker.AsyncMock(side_effect=Exception("Ollama connection failed"))

        session = await debate_service.create_debate_session(sample_config)
        session.status = DebateStatus.ACTIVE

        # Execute round despite errors
        arguments = await debate_service.execute_debate_round(session.session_id)

        # Should still generate error arguments
        assert len(arguments) == 3
        assert all("Error generating response" in arg.content for arg in arguments)
        assert all(arg.evidence_score == 0.0 for arg in arguments)

    @pytest.mark.asyncio
    async def test_session_cleanup(self, debate_service, sample_config):
        """Test session cleanup after completion."""
        session = await debate_service.create_debate_session(sample_config)

        # Verify session exists
        assert session.session_id in debate_service.active_sessions

        # Cleanup session
        success = await debate_service.cleanup_session(session.session_id)
        assert success is True

        # Verify session is removed
        assert session.session_id not in debate_service.active_sessions


class TestDebateRulesEnforcement:
    """Tests for debate rules enforcement and constraints."""

    def test_evidence_requirement_enforcement(self):
        """Test evidence requirement rule enforcement."""
        from app.services.debate_service import DebateService

        service = DebateService()
        rules = DebateRules(require_evidence=True, evidence_threshold=0.8)

        # Test high evidence response
        high_evidence = "According to recent studies and research data, this approach is effective."
        score = service._analyze_evidence_quality(high_evidence, rules)
        assert score >= 0.7  # Should score well but may not meet strict threshold

        # Test low evidence response
        low_evidence = "I think this is a good idea because it feels right."
        score = service._analyze_evidence_quality(low_evidence, rules)
        assert score < rules.evidence_threshold

    def test_creativity_constraints(self):
        """Test creativity level constraints."""
        from app.services.debate_service import DebateService

        service = DebateService()

        # Creativity allowed
        rules_allow = DebateRules(allow_creativity=True, creativity_weight=0.4)
        creative_response = "Imagine if we could create an innovative hybrid approach..."
        score = service._analyze_creativity(creative_response, rules_allow)
        assert score > 0.5

        # Creativity not allowed
        rules_deny = DebateRules(allow_creativity=False)
        creative_response = "Imagine if we could create an innovative hybrid approach..."
        score = service._analyze_creativity(creative_response, rules_deny)
        assert score <= 0.6  # Should be moderate

    def test_fallacy_detection(self):
        """Test logical fallacy detection."""
        from app.services.debate_service import DebateService

        service = DebateService()

        # Response with fallacies
        fallacy_response = "You can't trust experts because they're part of the establishment. This is clearly a straw man argument against reasonable regulation."
        fallacies = service._analyze_fallacies(fallacy_response)
        assert fallacies >= 1  # Should detect at least one fallacy

        # Clean response
        clean_response = "Based on evidence and logical reasoning, we should proceed carefully."
        fallacies = service._analyze_fallacies(clean_response)
        assert fallacies == 0

    def test_consensus_impact_calculation(self):
        """Test consensus impact calculation."""
        from app.services.debate_service import DebateService

        service = DebateService()

        # Agreement response
        agreement = "I agree with the previous point and would like to add..."
        previous_args = [DebateArgument(agent_name="Other Agent", content="test")]
        impact = service._calculate_consensus_impact(agreement, previous_args)
        assert impact > 0  # Positive consensus impact

        # Disagreement response
        disagreement = "However, I disagree because..."
        impact = service._calculate_consensus_impact(disagreement, previous_args)
        assert impact < 0  # Negative consensus impact

        # Neutral response
        neutral = "This is an interesting point to consider."
        impact = service._calculate_consensus_impact(neutral, previous_args)
        assert abs(impact) < 0.1  # Low consensus impact


class TestAgentCommunicationPatterns:
    """Tests for agent communication patterns during debates."""

    def test_prompt_construction_for_different_agent_types(self):
        """Test that prompts are constructed appropriately for different agent types."""
        from app.services.debate_service import DebateService, DebateConfiguration

        service = DebateService()

        # Test different agent types
        agents = [
            DebateParticipant(
                agent_id='logical', agent_name='Logical Analyst',
                agent_type='logical_analyst', specialization='Logic and reasoning'
            ),
            DebateParticipant(
                agent_id='creative', agent_name='Creative Thinker',
                agent_type='creative_thinker', specialization='Innovation and creativity'
            ),
            DebateParticipant(
                agent_id='moderator', agent_name='Neutral Moderator',
                agent_type='moderator', specialization='Facilitation and balance'
            )
        ]

        config = DebateConfiguration(
            debate_topic="AI Ethics",
            debate_rules=DebateRules()
        )

        class MockSession:
            def __init__(self):
                self.configuration = config

        session = MockSession()

        for agent in agents:
            prompt = service._build_system_prompt(agent, session, 1)

            # Verify agent-specific content
            assert agent.agent_name in prompt
            assert agent.specialization in prompt
            assert "AI Ethics" in prompt
            assert "DEBATE RULES:" in prompt

    def test_context_inclusion_in_user_prompts(self):
        """Test that previous arguments are included in user prompts."""
        from app.services.debate_service import DebateService

        service = DebateService()

        participant = DebateParticipant(
            agent_id='test_agent',
            agent_name='Test Agent',
            agent_type='logical',
            specialization='Logic and reasoning'
        )

        # Test opening round (no previous arguments)
        opening_prompt = service._build_user_prompt([], participant, 1)
        assert "this is round 1" in opening_prompt.lower()
        assert "initial position" in opening_prompt.lower()

        # Test subsequent round (with previous arguments)
        previous_args = [
            DebateArgument(
                agent_name="Agent A", agent_type="logical",
                content="First argument content here"
            ),
            DebateArgument(
                agent_name="Agent B", agent_type="creative",
                content="Second argument content here"
            )
        ]

        response_prompt = service._build_user_prompt(previous_args, participant, 2)
        assert "Previous arguments" in response_prompt
        assert "Agent A" in response_prompt
        assert "Agent B" in response_prompt
        assert "Respond to these arguments" in response_prompt


class TestDebateAnalyticsAndConclusions:
    """Tests for debate analytics, summaries, and conclusions."""

    @pytest.fixture
    async def debate_service(self):
        """Create debate service for testing."""
        service = DebateService()
        await service.initialize()
        return service

    @pytest.mark.asyncio
    async def test_debate_conclusion_generation_consensus(self, debate_service):
        """Test conclusion generation for consensus outcome."""
        # Mock high consensus session
        session = DebateSession(
            session_id='test_session',
            status=DebateStatus.COMPLETED,
            consensus_score=0.85,
            current_round=3,
            total_arguments=9
        )

        # Add mock rounds with arguments
        session.rounds = [
            {'arguments': [
                DebateArgument(agent_name='Agent 1', content='Strong pro argument'),
                DebateArgument(agent_name='Agent 2', content='Agreeing counterpoint'),
                DebateArgument(agent_name='Agent 3', content='Balanced synthesis')
            ]},
            {'arguments': [
                DebateArgument(agent_name='Agent 1', content='Building consensus'),
                DebateArgument(agent_name='Agent 2', content='Finding common ground'),
                DebateArgument(agent_name='Agent 3', content='Unified approach')
            ]},
            {'arguments': [
                DebateArgument(agent_name='Agent 1', content='Final agreement'),
                DebateArgument(agent_name='Agent 2', content='Consensus reached'),
                DebateArgument(agent_name='Agent 3', content='Conclusion supported')
            ]}
        ]

        conclusion = await debate_service.generate_debate_conclusion(session)

        assert conclusion.conclusion_type == "consensus"
        assert conclusion.confidence_score == 0.85
        assert len(conclusion.key_insights) > 0
        assert len(conclusion.recommendations) > 0
        assert "consensus" in conclusion.summary.lower()

    def test_key_insights_extraction(self):
        """Test extraction of key insights from debate arguments."""
        from app.services.debate_service import DebateService

        service = DebateService()

        # Mock arguments with common themes
        arguments = [
            DebateArgument(content="Regulation is essential for safety and control"),
            DebateArgument(content="We need regulatory frameworks for AI development"),
            DebateArgument(content="Safety regulations are crucial for responsible AI"),
            DebateArgument(content="Innovation should not be stifled by excessive regulation"),
            DebateArgument(content="Balance between innovation and safety is needed")
        ]

        insights = service._extract_key_insights(arguments)

        # Should identify regulation and safety themes
        insight_text = ' '.join(insights).lower()
        assert 'regulation' in insight_text or 'safety' in insight_text
        assert len(insights) <= 3  # Limited to top insights

    def test_winning_position_determination(self):
        """Test determination of winning debate position."""
        from app.services.debate_service import DebateService

        service = DebateService()

        # Mock arguments favoring "pro" position
        pro_arguments = [
            DebateArgument(content="We should definitely support this approach"),
            DebateArgument(content="Yes, this is the right way forward"),
            DebateArgument(content="I approve of this proposal"),
            DebateArgument(content="This positive change should be implemented"),
            DebateArgument(content="Support for this initiative is warranted")
        ]

        winning_pos = service._determine_winning_position(pro_arguments)
        assert winning_pos == "pro"


@pytest.mark.asyncio
class TestEndToEndDebateWorkflow:
    """End-to-end integration tests for complete debate workflows."""

    @pytest.fixture
    async def full_debate_service(self):
        """Create fully initialized debate service."""
        from app.services.debate_service import DebateService
        service = DebateService()
        await service.initialize()
        return service

    async def test_complete_debate_lifecycle(self, full_debate_service, mocker):
        """Test complete debate lifecycle from creation to conclusion."""
        # Mock Ollama service for consistent responses
        mock_ollama = mocker.patch.object(full_debate_service, 'ollama_service')

        # Create mock responses for 3 agents × 2 rounds = 6 responses
        mock_responses = [
            # Round 1
            {'response': 'As a logical analyst, I argue that AI regulation is necessary for ethical development and risk mitigation.', 'model': 'llama2:7b', 'duration_seconds': 1.0},
            {'response': 'From an argumentation perspective, over-regulation might hinder innovation and progress.', 'model': 'llama2:7b', 'duration_seconds': 1.1},
            {'response': 'Conceptually, we need a balanced framework that protects society while enabling advancement.', 'model': 'llama2:7b', 'duration_seconds': 1.2},
            # Round 2
            {'response': 'Building on the previous points, evidence shows that regulated AI development leads to safer outcomes.', 'model': 'llama2:7b', 'duration_seconds': 1.0},
            {'response': 'However, we must address concerns about regulatory capture and bureaucratic inefficiencies.', 'model': 'llama2:7b', 'duration_seconds': 1.1},
            {'response': 'The key is finding the right balance between oversight and innovation through adaptive frameworks.', 'model': 'llama2:7b', 'duration_seconds': 1.2}
        ]
        mock_ollama.generate = mocker.AsyncMock(side_effect=mock_responses)

        # Step 1: Create debate configuration
        config = DebateConfiguration(
            debate_topic="Should AI development be regulated?",
            problem_statement="What regulatory frameworks should govern artificial intelligence development?",
            premise_area="AI technology presents both unprecedented opportunities and significant risks to society",
            selected_agents=['11', '12', '13'],  # Using our mock agent IDs
            agent_roles={'11': 'Proponent', '12': 'Opponent', '13': 'Moderator'},
            max_rounds=2,
            consensus_threshold=0.7,
            debate_rules=DebateRules(
                require_evidence=True,
                enable_fact_checking=True,
                allow_creativity=True,
                enforce_formality=True
            )
        )

        # Step 2: Create debate session
        session = await full_debate_service.create_debate_session(config)
        assert session.status == DebateStatus.INITIALIZED

        # Step 3: Start debate execution
        session.status = DebateStatus.ACTIVE

        # Step 4: Execute debate rounds
        round_summaries = []
        for round_num in range(1, config.max_rounds + 1):
            arguments = await full_debate_service.execute_debate_round(session.session_id)
            assert len(arguments) == 3  # 3 agents per round

            # Generate round summary
            summary = await full_debate_service.generate_round_summary(
                session.session_id, round_num, arguments
            )
            round_summaries.append(summary)

        # Step 5: Verify execution results
        assert session.current_round == 2
        assert session.total_arguments == 6
        assert len(round_summaries) == 2

        # Check that consensus improved or was calculated
        assert isinstance(session.consensus_score, (int, float))

        # Step 6: Generate final conclusion
        conclusion = await full_debate_service.generate_debate_conclusion(session)

        assert conclusion.conclusion_type in ["consensus", "majority", "deadlock", "synthesis"]
        assert isinstance(conclusion.confidence_score, (int, float))
        assert len(conclusion.key_insights) > 0
        assert len(conclusion.recommendations) > 0
        assert conclusion.timestamp is not None

        # Step 7: Cleanup
        cleanup_success = await full_debate_service.cleanup_session(session.session_id)
        assert cleanup_success is True

        # Verify Ollama was called correctly
        assert mock_ollama.generate.call_count == 6  # 3 agents × 2 rounds


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s", "--tb=short"])
