import React, { useState, useEffect } from "react";
import {
  Form,
  Input,
  Select,
  Button,
  Card,
  message,
  Space,
  Typography,
} from "antd";
import { useAuth } from "../../contexts/AuthContext";
import { api } from "../../services/api";

const { Title } = Typography;
const { Option } = Select;

interface CommunicationPreference {
  default_channel: string;
  email_template?: string;
  sms_template?: string;
  whatsapp_template?: string;
  telegram_template?: string;
  working_hours_start?: string;
  working_hours_end?: string;
  max_daily_outreach?: number;
}

const OutreachConfig: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const { token } = useAuth();

  const fetchPreferences = React.useCallback(async () => {
    try {
      const response = await api.get<CommunicationPreference>(
        "/api/v1/preferences",
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );
      form.setFieldsValue(response.data);
    } catch (error) {
      message.error("Failed to fetch preferences");
    }
  }, [token, form]);

  useEffect(() => {
    fetchPreferences();
  }, [fetchPreferences]);

  const handleSubmit = async (values: CommunicationPreference) => {
    setLoading(true);
    try {
      await api.put("/api/v1/preferences", values, {
        headers: { Authorization: `Bearer ${token}` },
      });
      message.success("Preferences updated successfully");
    } catch (error) {
      message.error("Failed to update preferences");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "24px" }}>
      <Title level={2}>Outreach Configuration</Title>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            default_channel: "email",
            max_daily_outreach: 100,
          }}
        >
          <Form.Item
            name="default_channel"
            label="Default Channel"
            rules={[{ required: true }]}
          >
            <Select>
              <Option value="email">Email</Option>
              <Option value="sms">SMS</Option>
              <Option value="whatsapp">WhatsApp</Option>
              <Option value="telegram">Telegram</Option>
            </Select>
          </Form.Item>

          <Form.Item name="email_template" label="Email Template">
            <Input.TextArea rows={4} />
          </Form.Item>

          <Form.Item name="sms_template" label="SMS Template">
            <Input.TextArea rows={2} />
          </Form.Item>

          <Form.Item name="whatsapp_template" label="WhatsApp Template">
            <Input.TextArea rows={3} />
          </Form.Item>

          <Form.Item name="telegram_template" label="Telegram Template">
            <Input.TextArea rows={3} />
          </Form.Item>

          <Space>
            <Form.Item name="working_hours_start" label="Working Hours Start">
              <Input type="time" />
            </Form.Item>

            <Form.Item name="working_hours_end" label="Working Hours End">
              <Input type="time" />
            </Form.Item>
          </Space>

          <Form.Item
            name="max_daily_outreach"
            label="Max Daily Outreach"
            rules={[{ required: true }]}
          >
            <Input type="number" min={1} />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              Save Preferences
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default OutreachConfig;
