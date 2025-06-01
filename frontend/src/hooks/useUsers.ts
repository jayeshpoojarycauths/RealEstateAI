import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";
import { Role } from "../types/auth";
import { logger } from "../utils/logger";

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: Role;
  isActive: boolean;
}

export interface CreateUserData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role: Role;
}

export interface UpdateUserData {
  email?: string;
  firstName?: string;
  lastName?: string;
  role?: Role;
  isActive?: boolean;
}

export const useUsers = () => {
  const queryClient = useQueryClient();
  const {
    data: users,
    isLoading,
    error,
  } = useQuery<User[]>({
    queryKey: ["users"],
    queryFn: async () => {
      try {
        const response = await api.get("/api/v1/users");
        return response.data;
      } catch (err) {
        logger.error("Failed to fetch users", err);
        throw err;
      }
    },
  });

  const createUserMutation = useMutation({
    mutationFn: async (userData: CreateUserData) => {
      try {
        const response = await api.post("/api/v1/users", userData);
        return response.data;
      } catch (err) {
        logger.error("Failed to create user", err, { email: userData.email });
        setError(err as Error);
        throw err;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const updateUserMutation = useMutation({
    mutationFn: async ({
      userId,
      userData,
    }: {
      userId: string;
      userData: UpdateUserData;
    }) => {
      try {
        const response = await api.patch(`/api/v1/users/${userId}`, userData);
        return response.data;
      } catch (err) {
        logger.error("Failed to update user", err, { userId });
        setError(err as Error);
        throw err;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const deleteUserMutation = useMutation({
    mutationFn: async (userId: string) => {
      try {
        await api.delete(`/api/v1/users/${userId}`);
      } catch (err) {
        logger.error("Failed to delete user", err, { userId });
        setError(err as Error);
        throw err;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const createUser = async (userData: CreateUserData) => {
    return createUserMutation.mutateAsync(userData);
  };

  const updateUser = async (userId: string, userData: UpdateUserData) => {
    return updateUserMutation.mutateAsync({ userId, userData });
  };

  const deleteUser = async (userId: string) => {
    return deleteUserMutation.mutateAsync(userId);
  };

  return {
    users,
    isLoading,
    error,
    createUser,
    updateUser,
    deleteUser,
  };
};
