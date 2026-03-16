import { customFetch } from "@/api/mutator";

export interface GroupTask {
  id: string;
  title: string;
  description?: string | null;
  status: string;
  priority: string;
  board_group_id: string;
  created_at: string;
  updated_at: string;
}

export interface GroupTaskCreate {
  title: string;
  description?: string | null;
  status?: string;
  priority?: string;
}

export interface GroupTaskUpdate {
  title?: string;
  description?: string | null;
  status?: string;
  priority?: string;
}

export async function listGroupTasks(groupId: string): Promise<GroupTask[]> {
  const res = await customFetch<{ data: { items: GroupTask[] }; status: number }>(
    `/api/v1/board-groups/${groupId}/tasks?limit=100`,
    { method: "GET" },
  );
  return res.data?.items ?? [];
}

export async function createGroupTask(
  groupId: string,
  data: GroupTaskCreate,
): Promise<GroupTask> {
  const res = await customFetch<{ data: GroupTask; status: number }>(
    `/api/v1/board-groups/${groupId}/tasks`,
    { method: "POST", body: JSON.stringify(data) },
  );
  return res.data;
}

export async function updateGroupTask(
  groupId: string,
  taskId: string,
  data: GroupTaskUpdate,
): Promise<GroupTask> {
  const res = await customFetch<{ data: GroupTask; status: number }>(
    `/api/v1/board-groups/${groupId}/tasks/${taskId}`,
    { method: "PATCH", body: JSON.stringify(data) },
  );
  return res.data;
}

export async function deleteGroupTask(
  groupId: string,
  taskId: string,
): Promise<void> {
  await customFetch<{ data: unknown; status: number }>(
    `/api/v1/board-groups/${groupId}/tasks/${taskId}`,
    { method: "DELETE" },
  );
}

export interface TaskComment {
  id: string;
  message: string | null;
  author_name?: string | null;
  agent_id?: string | null;
  created_at: string;
}

export async function listGroupTaskComments(
  groupId: string,
  taskId: string,
): Promise<TaskComment[]> {
  const res = await customFetch<{ data: { items: TaskComment[] }; status: number }>(
    `/api/v1/board-groups/${groupId}/tasks/${taskId}/comments?limit=100`,
    { method: "GET" },
  );
  return res.data?.items ?? [];
}

export async function createGroupTaskComment(
  groupId: string,
  taskId: string,
  content: string,
): Promise<TaskComment> {
  const res = await customFetch<{ data: TaskComment; status: number }>(
    `/api/v1/board-groups/${groupId}/tasks/${taskId}/comments`,
    { method: "POST", body: JSON.stringify({ message: content }) },
  );
  return res.data;
}
