import React, { useState } from 'react';
import { Upload, Button, Table, Alert, Space, Typography } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';
import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../services/api';

const { Title } = Typography;

interface LeadUploadResponse {
  success_count: number;
  error_count: number;
  errors: string[];
}

const LeadUpload: React.FC = () => {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [response, setResponse] = useState<LeadUploadResponse | null>(null);
  const { token } = useAuth();

  const handleUpload = async () => {
    if (fileList.length === 0) return;

    const formData = new FormData();
    formData.append('file', fileList[0].originFileObj as File);

    setUploading(true);
    try {
      const result = await api.post<LeadUploadResponse>('/api/v1/leads/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`,
        },
      });
      setResponse(result.data);
      setFileList([]);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  const uploadProps = {
    onRemove: (file: UploadFile) => {
      const index = fileList.indexOf(file);
      const newFileList = fileList.slice();
      newFileList.splice(index, 1);
      setFileList(newFileList);
    },
    beforeUpload: (file: UploadFile) => {
      setFileList([file]);
      return false;
    },
    fileList,
    accept: '.csv,.xlsx',
  };

  const errorColumns = [
    {
      title: 'Error',
      dataIndex: 'error',
      key: 'error',
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>Upload Leads</Title>
      
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Alert
          message="File Requirements"
          description="Upload a CSV or Excel file with the following columns: name, email, phone, source. Optional columns: notes, status."
          type="info"
          showIcon
        />

        <Upload {...uploadProps}>
          <Button icon={<UploadOutlined />}>Select File</Button>
        </Upload>

        <Button
          type="primary"
          onClick={handleUpload}
          disabled={fileList.length === 0}
          loading={uploading}
          style={{ marginTop: 16 }}
        >
          {uploading ? 'Uploading' : 'Start Upload'}
        </Button>

        {response && (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Alert
              message={`Upload Complete: ${response.success_count} leads imported successfully`}
              type="success"
              showIcon
            />
            
            {response.error_count > 0 && (
              <>
                <Alert
                  message={`${response.error_count} errors occurred during import`}
                  type="warning"
                  showIcon
                />
                <Table
                  columns={errorColumns}
                  dataSource={response.errors.map((error, index) => ({
                    key: index,
                    error,
                  }))}
                  pagination={false}
                  size="small"
                />
              </>
            )}
          </Space>
        )}
      </Space>
    </div>
  );
};

export default LeadUpload; 