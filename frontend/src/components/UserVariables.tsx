import React, { useState, useEffect } from 'react';
import { Button, Input, Form, message } from 'antd';
import { fetchJSON, getServerUrl } from './utils';
import { PlusOutlined } from '@ant-design/icons';

const UserVariables = () => {
  const [secrets, setSecrets] = useState<string[]>([]);
  const [dynamicFields, setDynamicFields] = useState<Record<string, string>[]>([{ key: '', value: '' }]);
  const [loading, setLoading] = useState(false);
  const serverUrl = getServerUrl();
  const getUserSecretsUrl = `${serverUrl}/user/settings/secrets`;

  useEffect(() => {
    const fetchSecrets = async () => {
      setLoading(true);
      try {
        const response = await fetchJSON(getUserSecretsUrl, { method: 'GET' });
        if (response.status && Array.isArray(response.data)) {
          setSecrets(response.data);
        } else {
          throw new Error('Invalid response format');
        }
      } catch (error) {
        message.error('Failed to fetch secrets: ' + error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSecrets();
  }, []);

  const handleFieldChange = (index, keyOrValue, value) => {
    setDynamicFields((prevFields) => {
      const newFields = [...prevFields];
      newFields[index][keyOrValue] = value;
      if (index === prevFields.length - 1 && (newFields[index].key || newFields[index].value)) {
        newFields.push({ key: '', value: '' }); // Add a new field when the last field is edited
      }
      return newFields;
    });
  };

  const handleUpdateSecrets = async () => {
    setLoading(true);
    try {
      const payload = dynamicFields.reduce((acc, field) => {
        if (field.key && field.value) {
          acc[field.key] = field.value;
        }
        return acc;
      }, {});
      await fetchJSON(getUserSecretsUrl, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      });
      message.success('Secrets updated successfully');
      setDynamicFields([{ key: '', value: '' }]); // Reset for more additions
    } catch (error) {
      message.error('Failed to update secrets');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form layout="vertical" onFinish={handleUpdateSecrets}>
      {secrets.map((secret, index) => (
        <Form.Item key={index} label={secret}>
          <Input placeholder="***" disabled />
        </Form.Item>
      ))}
      {dynamicFields.map((field, index) => (
        <React.Fragment key={index}>
          <Form.Item
            label="Key"
            name={`key-${index}`}
            rules={[{ required: index !== dynamicFields.length - 1, message: 'Please input the key!' }]}
          >
            <Input value={field.key} onChange={(e) => handleFieldChange(index, 'key', e.target.value)} />
          </Form.Item>
          <Form.Item
            label="Value"
            name={`value-${index}`}
            rules={[{ required: index !== dynamicFields.length - 1, message: 'Please input the value!' }]}
          >
            <Input value={field.value} onChange={(e) => handleFieldChange(index, 'value', e.target.value)} />
          </Form.Item>
        </React.Fragment>
      ))}
      <Form.Item>
        <Button type="primary" htmlType="submit" loading={loading}>
          Update Secrets
        </Button>
      </Form.Item>
    </Form>
  );
};

export default UserVariables;
