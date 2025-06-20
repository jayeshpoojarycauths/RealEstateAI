import { api } from "../config/api";
import {
  Property,
  CreatePropertyDto,
  UpdatePropertyDto,
  PropertyFilters,
} from "../types/property";

export const propertyService = {
  getAll: async (filters?: PropertyFilters): Promise<Property[]> => {
    const { data } = await api.get("/properties", { params: filters });
    return data;
  },

  getById: async (id: string): Promise<Property> => {
    const { data } = await api.get(`/properties/${id}`);
    return data;
  },

  create: async (property: CreatePropertyDto): Promise<Property> => {
    const { data } = await api.post("/properties", property);
    return data;
  },

  update: async (property: UpdatePropertyDto): Promise<Property> => {
    const { id, ...updateData } = property;
    const { data } = await api.put(`/properties/${id}`, updateData);
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/properties/${id}`);
  },

  uploadImage: async (propertyId: string, file: File): Promise<string> => {
    const formData = new FormData();
    formData.append("image", file);
    const { data } = await api.post(
      `/properties/${propertyId}/images`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );
    return data;
  },

  deleteImage: async (propertyId: string, imageUrl: string): Promise<void> => {
    await api.delete(`/properties/${propertyId}/images`, {
      data: { imageUrl },
    });
  },

  uploadImages: async (id: string, images: File[]): Promise<Property> => {
    const formData = new FormData();
    images.forEach((image) => {
      formData.append("images", image);
    });
    const { data } = await api.post<Property>(
      `/properties/${id}/images`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );
    return data;
  },

  async getFeatured(): Promise<Property[]> {
    const { data } = await api.get<Property[]>("/properties/featured");
    return data;
  },

  async getSimilar(id: string): Promise<Property[]> {
    const { data } = await api.get<Property[]>(`/properties/${id}/similar`);
    return data;
  },

  async getByAgent(agentId: string): Promise<Property[]> {
    const { data } = await api.get<Property[]>(
      `/properties/byAgent/${agentId}`,
    );
    return data;
  },
};
