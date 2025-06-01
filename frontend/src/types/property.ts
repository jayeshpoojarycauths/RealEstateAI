export type PropertyStatus = 'available' | 'sold' | 'pending';
export type PropertyType = 'residential' | 'commercial' | 'land';

export interface Property {
  id: string;
  title: string;
  description: string;
  address: string;
  price: number;
  status: PropertyStatus;
  type: PropertyType;
  bedrooms?: number;
  bathrooms?: number;
  area: number;
  features: string[];
  images: string[];
  createdAt: string;
  updatedAt: string;
}

export interface CreatePropertyDto {
  title: string;
  description: string;
  address: string;
  price: number;
  status: PropertyStatus;
  type: PropertyType;
  bedrooms?: number;
  bathrooms?: number;
  area: number;
  features: string[];
  images: string[];
}

export interface UpdatePropertyDto extends Partial<CreatePropertyDto> {
  id: string;
}

export interface PropertyFilters {
  search?: string;
  status?: PropertyStatus;
  type?: PropertyType;
  minPrice?: number;
  maxPrice?: number;
  minArea?: number;
  maxArea?: number;
  bedrooms?: number;
  bathrooms?: number;
  features?: string[];
  page?: number;
  limit?: number;
  sortBy?: keyof Property;
  sortOrder?: 'asc' | 'desc';
} 