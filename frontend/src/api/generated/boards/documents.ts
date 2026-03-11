// Generated API types and hooks for board documents
import type { BoardDocumentRead, BoardDocumentCreate, BoardDocumentUpdate } from "@/api/generated/model";
import { useQuery, useMutation } from "@tanstack/react-query";

type ApiError = any;

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// List documents
export const useListBoardDocumentsApiV1BoardsBoardIdDocumentsGet = <TData = any, TError = ApiError>(
  boardId: string,
  params?: { limit?: number },
  options?: { query?: any }
) => {
  return useQuery<TData, TError>({
    queryKey: [`/boards/${boardId}/documents`, params],
    queryFn: async () => {
      const response = await fetch(
        `${BASE_URL}/boards/${boardId}/documents?limit=${params?.limit || 100}`,
        {
          headers: {
            Authorization: `Bearer ${typeof window !== "undefined" ? localStorage.getItem("token") : ""}`,
          },
        }
      );
      if (!response.ok) throw new Error("Failed to fetch documents");
      return response.json();
    },
    ...options?.query,
  });
};

// Create document
export const useCreateBoardDocumentApiV1BoardsBoardIdDocumentsPost = <TError = ApiError>(
  boardId: string,
  options?: { mutation?: any }
) => {
  return useMutation<any, TError, { data?: BoardDocumentCreate } | any>({
    mutationFn: async (payload) => {
      const data = (payload as any).data || payload;
      const response = await fetch(`${BASE_URL}/boards/${boardId}/documents`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${typeof window !== "undefined" ? localStorage.getItem("token") : ""}`,
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error("Failed to create document");
      return response.json();
    },
    ...options?.mutation,
  });
};

// Update document
export const useUpdateBoardDocumentApiV1BoardsBoardIdDocumentsDocIdPatch = <TError = ApiError>(
  boardId: string,
  docId?: string,
  options?: { mutation?: any }
) => {
  return useMutation<any, TError, { board_id: string; doc_id: string; data: Partial<BoardDocumentUpdate> }>({
    mutationFn: async ({ board_id, doc_id, data }) => {
      const response = await fetch(`${BASE_URL}/boards/${board_id}/documents/${doc_id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${typeof window !== "undefined" ? localStorage.getItem("token") : ""}`,
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error("Failed to update document");
      return response.json();
    },
    ...options?.mutation,
  });
};

// Delete document
export const useDeleteBoardDocumentApiV1BoardsBoardIdDocumentsDocIdDelete = <TError = ApiError>(
  boardId: string,
  options?: { mutation?: any }
) => {
  return useMutation<void, TError, { board_id: string; doc_id: string }>({
    mutationFn: async ({ board_id, doc_id }) => {
      const response = await fetch(`${BASE_URL}/boards/${board_id}/documents/${doc_id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${typeof window !== "undefined" ? localStorage.getItem("token") : ""}`,
        },
      });
      if (!response.ok) throw new Error("Failed to delete document");
    },
    ...options?.mutation,
  });
};
