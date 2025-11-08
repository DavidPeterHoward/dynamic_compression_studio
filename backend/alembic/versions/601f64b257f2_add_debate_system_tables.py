"""add_debate_system_tables

Revision ID: 601f64b257f2
Revises: 50bf854e8c17
Create Date: 2025-11-08 17:17:07.686416

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '601f64b257f2'
down_revision: Union[str, None] = '50bf854e8c17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create debate_sessions table
    op.create_table('debate_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), onupdate=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('status', sa.Enum('INITIALIZED', 'ACTIVE', 'PAUSED', 'COMPLETED', 'CONSENSUS_REACHED', name='debate_status'), nullable=False),
        sa.Column('debate_topic', sa.Text(), nullable=False),
        sa.Column('problem_statement', sa.Text(), nullable=False),
        sa.Column('premise_area', sa.Text(), nullable=False),
        sa.Column('debate_mode', sa.Enum('STRUCTURED', 'FREEFORM', 'AUTONOMOUS', name='debate_mode'), nullable=False),
        sa.Column('max_rounds', sa.Integer(), nullable=False),
        sa.Column('max_iterations_per_round', sa.Integer(), nullable=False),
        sa.Column('iterations_per_agent', sa.Integer(), nullable=False),
        sa.Column('consensus_threshold', sa.Float(), nullable=False),
        sa.Column('time_limit_per_argument', sa.Integer(), nullable=False),
        sa.Column('response_timeout', sa.Integer(), nullable=False),
        sa.Column('selected_agents', sa.JSON(), nullable=False),
        sa.Column('agent_roles', sa.JSON(), nullable=True),
        sa.Column('ollama_model', sa.String(length=100), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('max_tokens', sa.Integer(), nullable=False),
        sa.Column('system_prompt_template', sa.Text(), nullable=True),
        sa.Column('enable_detailed_logging', sa.Boolean(), nullable=False),
        sa.Column('export_format', sa.String(length=10), nullable=False),
        sa.Column('real_time_updates', sa.Boolean(), nullable=False),
        sa.Column('debate_rules', sa.JSON(), nullable=False),
        sa.Column('current_round', sa.Integer(), nullable=False),
        sa.Column('total_arguments', sa.Integer(), nullable=False),
        sa.Column('consensus_score', sa.Float(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )

    # Create indexes for debate_sessions
    op.create_index(op.f('ix_debate_sessions_session_id'), 'debate_sessions', ['session_id'], unique=False)

    # Create debate_participants table
    op.create_table('debate_participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), onupdate=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('agent_id', sa.String(length=255), nullable=False),
        sa.Column('agent_name', sa.String(length=255), nullable=False),
        sa.Column('agent_type', sa.String(length=100), nullable=False),
        sa.Column('specialization', sa.Text(), nullable=True),
        sa.Column('position', sa.String(length=50), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('arguments_made', sa.Integer(), nullable=False),
        sa.Column('rebuttals_given', sa.Integer(), nullable=False),
        sa.Column('fallacies_identified', sa.Integer(), nullable=False),
        sa.Column('strength_score', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['debate_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create debate_rounds table
    op.create_table('debate_rounds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), onupdate=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('arguments_count', sa.Integer(), nullable=False),
        sa.Column('consensus_score', sa.Float(), nullable=False),
        sa.Column('evidence_quality_avg', sa.Float(), nullable=False),
        sa.Column('creativity_level_avg', sa.Float(), nullable=False),
        sa.Column('key_points_discussed', sa.JSON(), nullable=True),
        sa.Column('round_summary', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['debate_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create debate_arguments table
    op.create_table('debate_arguments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), onupdate=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('participant_id', sa.Integer(), nullable=False),
        sa.Column('round_id', sa.Integer(), nullable=True),
        sa.Column('argument_id', sa.String(length=255), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('evidence_score', sa.Float(), nullable=False),
        sa.Column('creativity_score', sa.Float(), nullable=False),
        sa.Column('fallacies_detected', sa.Integer(), nullable=False),
        sa.Column('consensus_impact', sa.Float(), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('argument_type', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['participant_id'], ['debate_participants.id'], ),
        sa.ForeignKeyConstraint(['round_id'], ['debate_rounds.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['debate_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('argument_id')
    )

    # Create indexes for debate_arguments
    op.create_index(op.f('ix_debate_arguments_argument_id'), 'debate_arguments', ['argument_id'], unique=False)

    # Create debate_conclusions table
    op.create_table('debate_conclusions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), onupdate=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('conclusion_type', sa.String(length=50), nullable=False),
        sa.Column('winning_position', sa.String(length=100), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('final_consensus_score', sa.Float(), nullable=False),
        sa.Column('key_insights', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('total_rounds', sa.Integer(), nullable=False),
        sa.Column('total_arguments', sa.Integer(), nullable=False),
        sa.Column('average_evidence_score', sa.Float(), nullable=True),
        sa.Column('average_creativity_score', sa.Float(), nullable=True),
        sa.Column('dominant_agent', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['debate_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )

    # Create debate_analytics table
    op.create_table('debate_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), onupdate=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('analytics_type', sa.String(length=50), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=True),
        sa.Column('agent_id', sa.String(length=255), nullable=True),
        sa.Column('time_window', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['debate_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('debate_analytics')
    op.drop_table('debate_conclusions')
    op.drop_table('debate_arguments')
    op.drop_table('debate_rounds')
    op.drop_table('debate_participants')
    op.drop_table('debate_sessions')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS debate_status")
    op.execute("DROP TYPE IF EXISTS debate_mode")
