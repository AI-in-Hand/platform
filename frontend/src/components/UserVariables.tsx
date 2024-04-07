import React, { useState, useEffect } from 'react';
import { Button, Input, Form, message } from 'antd';
import { fetchJSON } from './utils';

const UserVariables = () => {
  const [secrets, setSecrets] = useState<string[]>([]);
  const [dynamicFields, setDynamicFields] = useState<Record<string, string>[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSecrets = async () => {
      setLoading(true);
      try {
        const response = await fetchJSON('/user/settings/secrets', { method: 'GET' });
        setSecrets(response);
      } catch (error) {
        message.error('Failed to fetch secrets');
      } finally {
        setLoading(false);
      }
    };

    fetchSecrets();
  }, []);

  const handleAddField = () => {
    setDynamicFields([...dynamicFields, { key: '', value: '' }]);
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
      const updatedSecrets = await fetchJSON('/user/settings/secrets', {
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

  useEffect(() => {
    if (dynamicFields.length === 0 || dynamicFields[dynamicFields.length - 1].key || dynamicFields[dynamicFields.length - 1].value) {
      handleAddField();
    }
  }, [dynamicFields]);

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
            rules={[{ required: true, message: 'Please input the key!' }]}
          >
            <Input value={field.key} onChange={(e) => {
              const newFields = [...dynamicFields];
              newFields[index].key = e.target.value;
              setDynamicFields(newFields);
            }} />
          </Form.Item>
          <Form.Item
            label="Value"
            name={`value-${index}`}
            rules={[{ required: true, message: 'Please input the value!' }]}
          >
            <Input value={field.value} onChange={(e) => {
              const newFields = [...dynamicFields];
              newFields[index].value = e.target.value;
              setDynamicFields(newFields);
            }} />
          </Form.Item>
        </React.Fragment>
      ))}
      <Button type="primary" htmlType="submit" loading={loading}>
        Update Secrets
      </Button>
    </Form>
  );
};

export default UserVariables;
