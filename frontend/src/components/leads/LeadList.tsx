import React, { useState, useEffect } from "react";
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
  Tag,
  DatePicker,
  Row,
  Col,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined,
  PhoneOutlined,
  MailOutlined,
} from "@ant-design/icons";
import { useAuth } from "../../contexts/AuthContext";
import { LeadStatus, LeadSource } from "../../types/lead";
import api from "../../services/api";

const { Option } = Select;
const { RangePicker } = DatePicker;

interface Lead {
  id: number;
  name: string;
  email: string;
  phone: string;
  status: LeadStatus;
  source: LeadSource;
  notes: string;
  assigned_to?: number;
  created_at: string;
  updated_at: string;
}

interface LeadFilter {
  status?: LeadStatus;
  source?: LeadSource;
  search?: string;
  date_range?: [string, string];
}

const LeadList: React.FC = () => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingLead, setEditingLead] = useState<Lead | null>(null);
  const [filters, setFilters] = useState<LeadFilter>({});
  const [form] = Form.useForm();
  const { token } = useAuth();

  const fetchLeads = React.useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.get("/api/v1/leads/", {
        params: filters,
        headers: { Authorization: `Bearer ${token}` },
      });
      setLeads(response.data);
    } catch (error) {
      message.error("Failed to fetch leads");
    } finally {
      setLoading(false);
    }
  }, [filters, token]);

  useEffect(() => {
    fetchLeads();
  }, [fetchLeads]);

  const handleCreate = () => {
    setEditingLead(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (lead: Lead) => {
    setEditingLead(lead);
    form.setFieldsValue(lead);
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/api/v1/leads/${id}`);
      message.success("Lead deleted successfully");
      fetchLeads();
    } catch (error) {
      message.error("Failed to delete lead");
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      const method = editingLead ? "put" : "post";
      const url = editingLead
        ? `/api/v1/leads/${editingLead.id}`
        : "/api/v1/leads/";

      await api[method](url, values);
      message.success(
        `Lead ${editingLead ? "updated" : "created"} successfully`,
      );
      setModalVisible(false);
      fetchLeads();
    } catch (error) {
      message.error(`Failed to ${editingLead ? "update" : "create"} lead`);
    }
  };

  const handleFilterChange = (values: LeadFilter) => {
    setFilters(values);
  };

  const columns = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      render: (text: string, record: Lead) => (
        <Space>
          <UserOutlined />
          {text}
        </Space>
      ),
    },
    {
      title: "Contact",
      key: "contact",
      render: (record: Lead) => (
        <Space direction="vertical">
          <Space>
            <MailOutlined />
            {record.email}
          </Space>
          <Space>
            <PhoneOutlined />
            {record.phone}
          </Space>
        </Space>
      ),
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status: LeadStatus) => (
        <Tag
          color={
            status === LeadStatus.NEW
              ? "blue"
              : status === LeadStatus.CONTACTED
                ? "orange"
                : status === LeadStatus.QUALIFIED
                  ? "green"
                  : status === LeadStatus.CONVERTED
                    ? "purple"
                    : "red"
          }
        >
          {status}
        </Tag>
      ),
    },
    {
      title: "Source",
      dataIndex: "source",
      key: "source",
      render: (source: LeadSource) => (
        <Tag
          color={
            source === LeadSource.WEBSITE
              ? "blue"
              : source === LeadSource.REFERRAL
                ? "green"
                : source === LeadSource.SOCIAL_MEDIA
                  ? "purple"
                  : "orange"
          }
        >
          {source}
        </Tag>
      ),
    },
    {
      title: "Actions",
      key: "actions",
      render: (_: any, record: Lead) => (
        <Space>
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Button
            icon={<DeleteOutlined />}
            danger
            onClick={() => handleDelete(record.id)}
          />
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Form layout="inline" onFinish={handleFilterChange}>
          <Row gutter={16} style={{ width: "100%" }}>
            <Col span={6}>
              <Form.Item name="status">
                <Select placeholder="Status" allowClear>
                  {Object.values(LeadStatus).map((status) => (
                    <Option key={status} value={status}>
                      {status}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="source">
                <Select placeholder="Source" allowClear>
                  {Object.values(LeadSource).map((source) => (
                    <Option key={source} value={source}>
                      {source}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="search">
                <Input placeholder="Search leads" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="date_range">
                <RangePicker />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>

      <Button
        type="primary"
        icon={<PlusOutlined />}
        onClick={handleCreate}
        style={{ marginBottom: 16 }}
      >
        Create Lead
      </Button>

      <Table
        columns={columns}
        dataSource={leads}
        loading={loading}
        rowKey="id"
      />

      <Modal
        title={editingLead ? "Edit Lead" : "Create Lead"}
        visible={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} onFinish={handleSubmit} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email"
            rules={[{ required: true }, { type: "email" }]}
          >
            <Input />
          </Form.Item>

          <Form.Item name="phone" label="Phone" rules={[{ required: true }]}>
            <Input />
          </Form.Item>

          <Form.Item name="status" label="Status" rules={[{ required: true }]}>
            <Select>
              {Object.values(LeadStatus).map((status) => (
                <Option key={status} value={status}>
                  {status}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="source" label="Source" rules={[{ required: true }]}>
            <Select>
              {Object.values(LeadSource).map((source) => (
                <Option key={source} value={source}>
                  {source}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="notes" label="Notes">
            <Input.TextArea />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit">
              {editingLead ? "Update" : "Create"}
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default LeadList;
