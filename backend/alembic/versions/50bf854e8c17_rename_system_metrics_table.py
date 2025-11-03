"""rename_system_metrics_table

Revision ID: 50bf854e8c17
Revises: 434bebe9f1fb
Create Date: 2025-10-31 12:00:45.569945

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50bf854e8c17'
down_revision: Union[str, None] = '434bebe9f1fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename system_metrics to system_monitoring_metrics to avoid conflict
    op.rename_table('system_metrics', 'system_monitoring_metrics')


def downgrade() -> None:
    op.rename_table('system_monitoring_metrics', 'system_metrics')
