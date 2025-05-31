import React, { useState, useEffect } from 'react';
import {
    Table,
    Button,
    Modal,
    Form,
    Input,
    Select,
    Space,
    message,
    Card,
    Statistic,
    Row,
    Col,
    DatePicker
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, BarChartOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { ProjectType, ProjectStatus } from '../types/project';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import api from '../services/api';

const { Option } = Select;

interface Project {
    id: number;
    name: string;
    description: string;
    type: ProjectType;
    status: ProjectStatus;
    location: string;
    total_units: number;
    price_range: string;
    amenities: string[];
    created_at: string;
    updated_at: string;
}

interface ProjectStats {
    total_leads: number;
    active_leads: number;
    converted_leads: number;
    conversion_rate: number;
}

interface ProjectAnalytics {
    lead_trends: Array<{
        date: string;
        count: number;
    }>;
    status_distribution: Array<{
        status: string;
        count: number;
    }>;
}

const ProjectList: React.FC = () => {
    const [projects, setProjects] = useState<Project[]>([]);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingProject, setEditingProject] = useState<Project | null>(null);
    const [form] = Form.useForm();
    const { token } = useAuth();
    const [stats, setStats] = useState<ProjectStats | null>(null);
    const [analytics, setAnalytics] = useState<ProjectAnalytics | null>(null);
    const [selectedProject, setSelectedProject] = useState<number | null>(null);

    const fetchProjects = async () => {
        try {
            const response = await api.get('/api/v1/projects/');
            setProjects(response.data);
        } catch (error) {
            console.error('Error fetching projects:', error);
            message.error('Failed to fetch projects');
        }
    };

    const fetchProjectStats = async (projectId: number) => {
        try {
            const response = await api.get(`/api/v1/projects/${projectId}/stats`);
            setStats(response.data);
        } catch (error) {
            console.error('Error fetching project stats:', error);
            message.error('Failed to fetch project stats');
        }
    };

    const fetchProjectAnalytics = async (projectId: number) => {
        try {
            const response = await api.get(`/api/v1/projects/${projectId}/analytics`);
            setAnalytics(response.data);
        } catch (error) {
            console.error('Error fetching project analytics:', error);
            message.error('Failed to fetch project analytics');
        }
    };

    useEffect(() => {
        fetchProjects();
    }, [token]);

    const handleCreate = () => {
        setEditingProject(null);
        form.resetFields();
        setModalVisible(true);
    };

    const handleEdit = (project: Project) => {
        setEditingProject(project);
        form.setFieldsValue(project);
        setModalVisible(true);
    };

    const handleDelete = async (id: number) => {
        try {
            await api.delete(`/api/v1/projects/${id}`);
            message.success('Project deleted successfully');
            fetchProjects();
        } catch (error) {
            console.error('Error deleting project:', error);
            message.error('Failed to delete project');
        }
    };

    const handleSubmit = async (values: any) => {
        try {
            const method = editingProject ? 'PUT' : 'POST';
            const url = editingProject
                ? `/api/v1/projects/${editingProject.id}`
                : '/api/v1/projects/';

            await api.request(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                data: values
            });

            message.success(`Project ${editingProject ? 'updated' : 'created'} successfully`);
            setModalVisible(false);
            fetchProjects();
        } catch (error) {
            message.error(`Failed to ${editingProject ? 'update' : 'create'} project`);
        }
    };

    const handleViewAnalytics = async (projectId: number) => {
        setSelectedProject(projectId);
        await Promise.all([
            fetchProjectStats(projectId),
            fetchProjectAnalytics(projectId)
        ]);
    };

    const handleAssignLead = async (projectId: number, leadId: number) => {
        try {
            await api.post(`/api/v1/projects/${projectId}/leads/${leadId}`);
            message.success('Lead assigned successfully');
            fetchProjects();
        } catch (error) {
            console.error('Error assigning lead:', error);
            message.error('Failed to assign lead');
        }
    };

    const handleRemoveLead = async (projectId: number, leadId: number) => {
        try {
            await api.delete(`/api/v1/projects/${projectId}/leads/${leadId}`);
            message.success('Lead removed successfully');
            fetchProjects();
        } catch (error) {
            console.error('Error removing lead:', error);
            message.error('Failed to remove lead');
        }
    };

    const columns = [
        {
            title: 'Name',
            dataIndex: 'name',
            key: 'name',
        },
        {
            title: 'Type',
            dataIndex: 'type',
            key: 'type',
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
        },
        {
            title: 'Location',
            dataIndex: 'location',
            key: 'location',
        },
        {
            title: 'Total Units',
            dataIndex: 'total_units',
            key: 'total_units',
        },
        {
            title: 'Price Range',
            dataIndex: 'price_range',
            key: 'price_range',
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (_: any, record: Project) => (
                <Space>
                    <Button
                        icon={<EditOutlined />}
                        onClick={() => handleEdit(record)}
                    />
                    <Button
                        icon={<DeleteOutlined />}
                        danger
                        onClick={() => handleDelete(record.id)}
                    />
                    <Button
                        icon={<BarChartOutlined />}
                        onClick={() => handleViewAnalytics(record.id)}
                    />
                </Space>
            ),
        },
    ];

    return (
        <div>
            <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleCreate}
                style={{ marginBottom: 16 }}
            >
                Create Project
            </Button>

            <Table
                columns={columns}
                dataSource={projects}
                loading={loading}
                rowKey="id"
            />

            <Modal
                title={editingProject ? 'Edit Project' : 'Create Project'}
                visible={modalVisible}
                onCancel={() => setModalVisible(false)}
                footer={null}
            >
                <Form
                    form={form}
                    onFinish={handleSubmit}
                    layout="vertical"
                >
                    <Form.Item
                        name="name"
                        label="Name"
                        rules={[{ required: true }]}
                    >
                        <Input />
                    </Form.Item>

                    <Form.Item
                        name="description"
                        label="Description"
                    >
                        <Input.TextArea />
                    </Form.Item>

                    <Form.Item
                        name="type"
                        label="Type"
                        rules={[{ required: true }]}
                    >
                        <Select>
                            {Object.values(ProjectType).map(type => (
                                <Option key={type} value={type}>{type}</Option>
                            ))}
                        </Select>
                    </Form.Item>

                    <Form.Item
                        name="status"
                        label="Status"
                        rules={[{ required: true }]}
                    >
                        <Select>
                            {Object.values(ProjectStatus).map(status => (
                                <Option key={status} value={status}>{status}</Option>
                            ))}
                        </Select>
                    </Form.Item>

                    <Form.Item
                        name="location"
                        label="Location"
                        rules={[{ required: true }]}
                    >
                        <Input />
                    </Form.Item>

                    <Form.Item
                        name="total_units"
                        label="Total Units"
                    >
                        <Input type="number" />
                    </Form.Item>

                    <Form.Item
                        name="price_range"
                        label="Price Range"
                    >
                        <Input />
                    </Form.Item>

                    <Form.Item
                        name="amenities"
                        label="Amenities"
                    >
                        <Select mode="tags" />
                    </Form.Item>

                    <Form.Item>
                        <Button type="primary" htmlType="submit">
                            {editingProject ? 'Update' : 'Create'}
                        </Button>
                    </Form.Item>
                </Form>
            </Modal>

            {selectedProject && stats && (
                <Card title="Project Statistics" style={{ marginTop: 16 }}>
                    <Row gutter={16}>
                        <Col span={6}>
                            <Statistic title="Total Leads" value={stats.total_leads} />
                        </Col>
                        <Col span={6}>
                            <Statistic title="Active Leads" value={stats.active_leads} />
                        </Col>
                        <Col span={6}>
                            <Statistic title="Converted Leads" value={stats.converted_leads} />
                        </Col>
                        <Col span={6}>
                            <Statistic
                                title="Conversion Rate"
                                value={stats.conversion_rate}
                                suffix="%"
                            />
                        </Col>
                    </Row>
                </Card>
            )}

            {selectedProject && analytics && (
                <Card title="Project Analytics" style={{ marginTop: 16 }}>
                    <LineChart
                        width={800}
                        height={400}
                        data={analytics.lead_trends}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line
                            type="monotone"
                            dataKey="count"
                            stroke="#8884d8"
                            name="Lead Count"
                        />
                    </LineChart>
                </Card>
            )}
        </div>
    );
};

export default ProjectList; 