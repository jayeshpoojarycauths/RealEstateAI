import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { act } from "react-dom/test-utils";
import LeadList from "../LeadList";
import { AuthProvider } from "../../../contexts/AuthContext";
import api from "../../../services/api";
import { LeadStatus, LeadSource } from "../../../types/lead";

// Mock the api module
jest.mock("../../../services/api");

const mockLeads = [
  {
    id: 1,
    name: "John Doe",
    email: "john@example.com",
    phone: "1234567890",
    status: LeadStatus.NEW,
    source: LeadSource.WEBSITE,
    notes: "Test lead",
    created_at: "2024-03-20T10:00:00Z",
    updated_at: "2024-03-20T10:00:00Z",
  },
];

describe("LeadList Component", () => {
  beforeEach(() => {
    // Mock api.get to return mock leads
    (api.get as jest.Mock).mockResolvedValue({ data: mockLeads });
  });

  it("renders lead list", async () => {
    render(
      <AuthProvider>
        <LeadList />
      </AuthProvider>,
    );

    // Wait for the leads to be loaded
    await waitFor(() => {
      expect(screen.getByText("John Doe")).toBeInTheDocument();
    });
  });

  it("opens create lead modal", async () => {
    render(
      <AuthProvider>
        <LeadList />
      </AuthProvider>,
    );

    // Click create button
    const createButton = screen.getByText("Create Lead");
    fireEvent.click(createButton);

    // Check if modal is opened
    expect(screen.getByText("Create Lead")).toBeInTheDocument();
  });

  it("filters leads by status", async () => {
    render(
      <AuthProvider>
        <LeadList />
      </AuthProvider>,
    );

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText("John Doe")).toBeInTheDocument();
    });

    // Select status filter
    const statusSelect = screen.getByPlaceholderText("Status");
    fireEvent.mouseDown(statusSelect);
    fireEvent.click(screen.getByText(LeadStatus.NEW));

    // Verify api call with filter
    expect(api.get).toHaveBeenCalledWith("/api/v1/leads/", {
      params: { status: LeadStatus.NEW },
    });
  });

  it("handles lead deletion", async () => {
    // Mock successful deletion
    (api.delete as jest.Mock).mockResolvedValue({});

    render(
      <AuthProvider>
        <LeadList />
      </AuthProvider>,
    );

    // Wait for leads to load
    await waitFor(() => {
      expect(screen.getByText("John Doe")).toBeInTheDocument();
    });

    // Click delete button
    const deleteButton = screen.getByRole("button", { name: /delete/i });
    fireEvent.click(deleteButton);

    // Verify api call
    expect(api.delete).toHaveBeenCalledWith("/api/v1/leads/1");
  });

  it("handles lead creation", async () => {
    // Mock successful creation
    (api.post as jest.Mock).mockResolvedValue({
      data: {
        id: 2,
        name: "Jane Doe",
        email: "jane@example.com",
        phone: "0987654321",
        status: LeadStatus.NEW,
        source: LeadSource.WEBSITE,
        notes: "New lead",
        created_at: "2024-03-20T11:00:00Z",
        updated_at: "2024-03-20T11:00:00Z",
      },
    });

    render(
      <AuthProvider>
        <LeadList />
      </AuthProvider>,
    );

    // Open create modal
    const createButton = screen.getByText("Create Lead");
    fireEvent.click(createButton);

    // Fill form
    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Jane Doe" },
    });
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "jane@example.com" },
    });
    fireEvent.change(screen.getByLabelText("Phone"), {
      target: { value: "0987654321" },
    });

    // Submit form
    const submitButton = screen.getByText("Create");
    fireEvent.click(submitButton);

    // Verify api call
    expect(api.post).toHaveBeenCalledWith("/api/v1/leads/", {
      name: "Jane Doe",
      email: "jane@example.com",
      phone: "0987654321",
      status: LeadStatus.NEW,
      source: LeadSource.WEBSITE,
    });
  });

  it("handles API errors", async () => {
    // Mock API error
    (api.get as jest.Mock).mockRejectedValue(new Error("API Error"));

    render(
      <AuthProvider>
        <LeadList />
      </AuthProvider>,
    );

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText("Failed to fetch leads")).toBeInTheDocument();
    });
  });
});
