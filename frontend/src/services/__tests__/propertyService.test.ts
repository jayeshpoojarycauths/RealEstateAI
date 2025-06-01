import {
  propertyService,
  Property,
  CreatePropertyDto,
} from "../propertyService";
import { api } from "../api";

// Mock the api module
jest.mock("../api", () => ({
  api: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

describe("PropertyService", () => {
  const mockProperty: Property = {
    id: "1",
    title: "Test Property",
    address: "123 Test St",
    price: 500000,
    status: "available",
    type: "residential",
    bedrooms: 3,
    bathrooms: 2,
    area: 2000,
    createdAt: "2024-03-15T10:00:00Z",
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("getAll", () => {
    it("should fetch properties with filters", async () => {
      const mockResponse = { data: [mockProperty] };
      (api.get as jest.Mock).mockResolvedValue(mockResponse);

      const filters = {
        search: "test",
        status: "available" as const,
        type: "residential" as const,
      };

      const result = await propertyService.getAll(filters);

      expect(api.get).toHaveBeenCalledWith("/properties", { params: filters });
      expect(result).toEqual([mockProperty]);
    });

    it("should fetch properties without filters", async () => {
      const mockResponse = { data: [mockProperty] };
      (api.get as jest.Mock).mockResolvedValue(mockResponse);

      const result = await propertyService.getAll();

      expect(api.get).toHaveBeenCalledWith("/properties", {
        params: undefined,
      });
      expect(result).toEqual([mockProperty]);
    });
  });

  describe("getById", () => {
    it("should fetch a property by id", async () => {
      const mockResponse = { data: mockProperty };
      (api.get as jest.Mock).mockResolvedValue(mockResponse);

      const result = await propertyService.getById("1");

      expect(api.get).toHaveBeenCalledWith("/properties/1");
      expect(result).toEqual(mockProperty);
    });
  });

  describe("create", () => {
    it("should create a new property", async () => {
      const mockResponse = { data: mockProperty };
      (api.post as jest.Mock).mockResolvedValue(mockResponse);

      const newProperty: CreatePropertyDto = {
        title: "Test Property",
        address: "123 Test St",
        price: 500000,
        status: "available",
        type: "residential",
        bedrooms: 3,
        bathrooms: 2,
        area: 2000,
      };

      const result = await propertyService.create(newProperty);

      expect(api.post).toHaveBeenCalledWith("/properties", newProperty);
      expect(result).toEqual(mockProperty);
    });
  });

  describe("update", () => {
    it("should update an existing property", async () => {
      const mockResponse = { data: mockProperty };
      (api.put as jest.Mock).mockResolvedValue(mockResponse);

      const updateData = {
        id: "1",
        price: 550000,
      };

      const result = await propertyService.update(updateData);

      expect(api.put).toHaveBeenCalledWith("/properties/1", updateData);
      expect(result).toEqual(mockProperty);
    });
  });

  describe("delete", () => {
    it("should delete a property", async () => {
      (api.delete as jest.Mock).mockResolvedValue({});

      await propertyService.delete("1");

      expect(api.delete).toHaveBeenCalledWith("/properties/1");
    });
  });
});
