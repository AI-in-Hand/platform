import React, { useState, useEffect } from 'react';
import { Button, Input, Form, message } from 'antd';
import { fetchJSON } from './utils';

const UserSettings = () => {
  const [secrets, setSecrets] = useState<Record<string, string>>({});
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

  const handleUpdateSecrets = async (values: Record<string, string>) => {
    setLoading(true);
    try {
      const updatedSecrets = await fetchJSON('/user/settings/secrets', {
        method: 'PATCH',
        body: JSON.stringify(values),
      });
      setSecrets(updatedSecrets);
      message.success('Secrets updated successfully');
    } catch (error) {
      message.error('Failed to update secrets');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form onFinish={handleUpdateSecrets} layout="vertical">
      {Object.keys(secrets).map((key) => (
        <Form.Item key={key} label={key} name={key} initialValue={secrets[key]}>
          <Input />
        </Form.Item>
      ))}
      <Button type="primary" htmlType="submit" loading={loading}>
        Update Secrets
      </Button>
    </Form>
  );
};

export default UserSettings;
