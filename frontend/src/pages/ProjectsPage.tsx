import React, { useState, useEffect } from "react";
import {
  Card,
  CardHeader,
  CardBody,
  Typography,
  Button,
  Input,
  Spinner,
  Select,
  Option,
  Chip,
} from "@material-tailwind/react";
import {
  MagnifyingGlassIcon,
  PlusIcon,
  ChevronUpIcon,
  ChevronDownIcon,
} from "@heroicons/react/24/outline";
import { useMaterialTailwind } from "../hooks/useMaterialTailwind";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

interface Project {
  id: number;
  name: string;
  location: string;
  status: "planning" | "in_progress" | "completed" | "on_hold";
  progress: number;
  start_date: string;
  end_date: string;
  budget: number;
  description: string;
}

type SortField = "name" | "location" | "status" | "progress" | "start_date";
type SortDirection = "asc" | "desc";

export const ProjectsPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [currentPage, setCurrentPage] = useState(1);
  const [sortField, setSortField] = useState<SortField>("start_date");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");
  const itemsPerPage = 10;
  const navigate = useNavigate();
  const {
    getButtonProps,
    getCardProps,
    getCardBodyProps,
    getCardHeaderProps,
    getTypographyProps,
    getInputProps,
  } = useMaterialTailwind();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await api.get("/projects/");
      setProjects(response.data);
    } catch (error) {
      console.error("Error fetching projects:", error);
      throw new Error("Failed to fetch projects");
    }
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  const getStatusColor = (status: Project["status"]) => {
    switch (status) {
      case "planning":
        return "blue";
      case "in_progress":
        return "amber";
      case "completed":
        return "green";
      case "on_hold":
        return "red";
      default:
        return "blue-gray";
    }
  };

  const getStatusLabel = (status: Project["status"]) => {
    return status
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const filteredProjects = projects
    .filter((project) => {
      const matchesSearch =
        project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.location.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus =
        statusFilter === "all" || project.status === statusFilter;
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      const aValue = a[sortField];
      const bValue = b[sortField];
      const modifier = sortDirection === "asc" ? 1 : -1;
      return aValue > bValue ? modifier : -modifier;
    });

  const totalPages = Math.ceil(filteredProjects.length / itemsPerPage);
  const paginatedProjects = filteredProjects.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage,
  );

  const statusOptions = [
    { value: "all", label: "All Statuses" },
    { value: "planning", label: "Planning" },
    { value: "in_progress", label: "In Progress" },
    { value: "completed", label: "Completed" },
    { value: "on_hold", label: "On Hold" },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <Typography variant="h6" color="red" {...getTypographyProps()}>
          {error}
        </Typography>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Typography variant="h4" color="blue-gray" {...getTypographyProps()}>
          Projects
        </Typography>
        <Button
          variant="filled"
          color="blue"
          onClick={() => navigate("/projects/new")}
          {...getButtonProps()}
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Project
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="w-full md:w-72">
          <Input
            type="text"
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            icon={<MagnifyingGlassIcon className="h-5 w-5" />}
            {...getInputProps()}
          />
        </div>
        <div className="w-full md:w-72">
          <Select
            value={statusFilter}
            onChange={(value) => setStatusFilter(value as string)}
            label="Filter by Status"
          >
            {statusOptions.map((option) => (
              <Option key={option.value} value={option.value}>
                {option.label}
              </Option>
            ))}
          </Select>
        </div>
      </div>

      {/* Projects Table */}
      <Card {...getCardProps()}>
        <CardHeader
          variant="gradient"
          color="blue"
          className="mb-4 p-6"
          {...getCardHeaderProps()}
        >
          <Typography variant="h6" color="white" {...getTypographyProps()}>
            Project List
          </Typography>
        </CardHeader>
        <CardBody className="p-0" {...getCardBodyProps()}>
          <div className="overflow-x-auto">
            <table className="w-full min-w-max table-auto text-left">
              <thead>
                <tr>
                  <th
                    className="border-b border-blue-gray-100 bg-blue-gray-50 p-4 cursor-pointer"
                    onClick={() => handleSort("name")}
                  >
                    <div className="flex items-center">
                      <Typography
                        variant="small"
                        color="blue-gray"
                        className="font-normal leading-none opacity-70"
                        {...getTypographyProps()}
                      >
                        Name
                      </Typography>
                      {sortField === "name" &&
                        (sortDirection === "asc" ? (
                          <ChevronUpIcon className="h-4 w-4 ml-1" />
                        ) : (
                          <ChevronDownIcon className="h-4 w-4 ml-1" />
                        ))}
                    </div>
                  </th>
                  <th
                    className="border-b border-blue-gray-100 bg-blue-gray-50 p-4 cursor-pointer"
                    onClick={() => handleSort("location")}
                  >
                    <div className="flex items-center">
                      <Typography
                        variant="small"
                        color="blue-gray"
                        className="font-normal leading-none opacity-70"
                        {...getTypographyProps()}
                      >
                        Location
                      </Typography>
                      {sortField === "location" &&
                        (sortDirection === "asc" ? (
                          <ChevronUpIcon className="h-4 w-4 ml-1" />
                        ) : (
                          <ChevronDownIcon className="h-4 w-4 ml-1" />
                        ))}
                    </div>
                  </th>
                  <th
                    className="border-b border-blue-gray-100 bg-blue-gray-50 p-4 cursor-pointer"
                    onClick={() => handleSort("status")}
                  >
                    <div className="flex items-center">
                      <Typography
                        variant="small"
                        color="blue-gray"
                        className="font-normal leading-none opacity-70"
                        {...getTypographyProps()}
                      >
                        Status
                      </Typography>
                      {sortField === "status" &&
                        (sortDirection === "asc" ? (
                          <ChevronUpIcon className="h-4 w-4 ml-1" />
                        ) : (
                          <ChevronDownIcon className="h-4 w-4 ml-1" />
                        ))}
                    </div>
                  </th>
                  <th
                    className="border-b border-blue-gray-100 bg-blue-gray-50 p-4 cursor-pointer"
                    onClick={() => handleSort("progress")}
                  >
                    <div className="flex items-center">
                      <Typography
                        variant="small"
                        color="blue-gray"
                        className="font-normal leading-none opacity-70"
                        {...getTypographyProps()}
                      >
                        Progress
                      </Typography>
                      {sortField === "progress" &&
                        (sortDirection === "asc" ? (
                          <ChevronUpIcon className="h-4 w-4 ml-1" />
                        ) : (
                          <ChevronDownIcon className="h-4 w-4 ml-1" />
                        ))}
                    </div>
                  </th>
                  <th className="border-b border-blue-gray-100 bg-blue-gray-50 p-4">
                    <Typography
                      variant="small"
                      color="blue-gray"
                      className="font-normal leading-none opacity-70"
                      {...getTypographyProps()}
                    >
                      Actions
                    </Typography>
                  </th>
                </tr>
              </thead>
              <tbody>
                {paginatedProjects.map((project) => (
                  <tr key={project.id}>
                    <td className="p-4">
                      <Typography
                        variant="small"
                        color="blue-gray"
                        className="font-normal"
                        {...getTypographyProps()}
                      >
                        {project.name}
                      </Typography>
                    </td>
                    <td className="p-4">
                      <Typography
                        variant="small"
                        color="blue-gray"
                        className="font-normal"
                        {...getTypographyProps()}
                      >
                        {project.location}
                      </Typography>
                    </td>
                    <td className="p-4">
                      <Chip
                        value={getStatusLabel(project.status)}
                        color={getStatusColor(project.status)}
                        size="sm"
                      />
                    </td>
                    <td className="p-4">
                      <div className="w-full bg-blue-gray-50 rounded-full h-2.5">
                        <div
                          className="bg-blue-600 h-2.5 rounded-full"
                          style={{ width: `${project.progress}%` }}
                        ></div>
                      </div>
                      <Typography
                        variant="small"
                        color="blue-gray"
                        className="mt-1 font-normal"
                        {...getTypographyProps()}
                      >
                        {project.progress}%
                      </Typography>
                    </td>
                    <td className="p-4">
                      <Button
                        variant="text"
                        color="blue"
                        size="sm"
                        onClick={() => navigate(`/projects/${project.id}`)}
                        {...getButtonProps()}
                      >
                        View
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between p-4 border-t border-blue-gray-50">
              <Typography
                variant="small"
                color="blue-gray"
                className="font-normal"
                {...getTypographyProps()}
              >
                Page {currentPage} of {totalPages}
              </Typography>
              <div className="flex gap-2">
                <Button
                  variant="text"
                  color="blue"
                  size="sm"
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage(currentPage - 1)}
                  {...getButtonProps()}
                >
                  Previous
                </Button>
                <Button
                  variant="text"
                  color="blue"
                  size="sm"
                  disabled={currentPage === totalPages}
                  onClick={() => setCurrentPage(currentPage + 1)}
                  {...getButtonProps()}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
};
