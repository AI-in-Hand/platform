import React, { useState, useEffect } from 'react';
import { Form, Input, Button, message } from 'antd';
import { fetchJSON, getServerUrl } from './utils';

const UserVariables = () => {
  const [form] = Form.useForm();
  const [secrets, setSecrets] = useState<string[]>([]);
  const [hasNewSecrets, setHasNewSecrets] = useState(false);
  const serverUrl = getServerUrl();
  const getUserSecretsUrl = `${serverUrl}/user/settings/secrets`;

  useEffect(() => {
    fetchSecrets();
  }, []);

  const fetchSecrets = () => {
    const payLoad = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    };
    const onSuccess = (data: any) => {
      if (data && data.status) {
        setSecrets(data.data);
      } else {
        message.error(data.message);
      }
    };
    const onError = (err: any) => {
      message.error(err.message);
    };
    fetchJSON(getUserSecretsUrl, payLoad, onSuccess, onError);
  };

  const saveSecrets = (values: any) => {
    const updatedSecrets: { [key: string]: string } = {};
    Object.entries(values.newSecrets || {}).forEach(([_, { key, value }]) => {
      if (key && value) {
        updatedSecrets[key] = value;
      }
    });

    if (Object.keys(updatedSecrets).length === 0) {
      message.error('Please provide at least one secret');
      return;
    }

    const payLoad = {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updatedSecrets),
    };
    const onSuccess = (data: any) => {
      if (data && data.status) {
        message.success(data.message);
        fetchSecrets();
      } else {
        message.error(data.message);
      }
    };
    const onError = (err: any) => {
      message.error(err.message);
    };
    fetchJSON(getUserSecretsUrl, payLoad, onSuccess, onError);
  };

  const checkNewSecrets = (values: any) => {
    const hasNewSecrets = Object.entries(values.newSecrets || {}).some(
      ([_, { key, value }]) => key && value
    );
    setHasNewSecrets(hasNewSecrets);
  };

  return (
    <div>
      <h2>Settings</h2>
      <Form form={form} onFinish={saveSecrets} onValuesChange={checkNewSecrets}>
        {secrets.map((secret) => (
          <Form.Item
            key={secret}
            label={secret}
            name={secret}
            initialValue="***"
          >
            <Input.Password />
          </Form.Item>
        ))}
        <Form.List name="newSecrets">
          {(fields, { add, remove }) => (
            <>
              {fields.map(({ key, name, ...restField }) => (
                <div key={key} style={{ display: 'flex', marginBottom: 8 }}>
                  <Form.Item
                    {...restField}
                    name={[name, 'key']}
                    style={{ marginRight: 8 }}
                  >
                    <Input placeholder="Secret Name" />
                  </Form.Item>
                  <Form.Item {...restField} name={[name, 'value']}>
                    <Input.Password placeholder="Secret Value" />
                  </Form.Item>
                  <Button onClick={() => remove(name)}>Remove</Button>
                </div>
              ))}
              <Form.Item>
                <Button type="dashed" onClick={() => add()} block>
                  Add Secret
                </Button>
              </Form.Item>
            </>
          )}
        </Form.List>
        <Form.Item>
          <Button type="primary" htmlType="submit" disabled={!hasNewSecrets}>
            Save
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default UserVariables;
