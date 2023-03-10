from typing import List
from enum import Enum
from supabase import create_client

class DeploymentState(Enum):
    Generating = "generating"
    Deploying = "deploying"
    Finished = "finished"
    Error = "error"

class Database():
  def __init__(self, url: str, key: str):
    self.client = create_client(url, key)

  def push_logs(self, run_id: str, project_id: str, route_id: str, logs: List[str]) -> None:
    if len(logs) > 0:
      self.client.table('deployments').upsert(
        json={
          'id': run_id,
          'logs': logs,
          'project_id': project_id,
          'route_id': route_id,
          'state': DeploymentState.Generating.value,
        },
      ).execute()

  def update_state(self, run_id: str, state: DeploymentState) -> None:
    self.client.table('deployments').update(
      json={
        'id': run_id,
        'state': state.value,
      },
    ).execute()