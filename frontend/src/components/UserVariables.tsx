import React, { useState, useEffect } from 'react';
import { Form, Input, Button, message } from 'antd';
import { fetchJSON, getServerUrl } from './utils';

const UserVariables = () => {
  const [form] = Form.useForm();
  const [secrets, setSecrets] = useState<string[]>([]);
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
        form.setFieldsValue(data.data.reduce((acc, key) => ({ ...acc, [key]: '***' }), {}));
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
    Object.entries(values).forEach(([key, value]) => {
      if (value && value !== '***') {
        updatedSecrets[key] = value;
      }
    });
    const payLoad = {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updatedSecrets),
    };
    const onSuccess = (data: any) => {
      if (data && data.status) {
        message.success('Secrets updated successfully');
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

  return (
    <div>
      <h2>Settings</h2>
      <Form form={form} onFinish={saveSecrets}>
        {secrets.map((secret) => (
          <Form.Item key={secret} label={secret} name={secret}>
            <Input.Password />
          </Form.Item>
        ))}
        <Form.List name="newSecrets">
          {(fields, { add, remove }) => (
            <>
              {fields.map(({ key, name, ...restField }) => (
                <div key={key} style={{ display: 'flex', marginBottom: 8 }}>
                  <Form.Item {...restField} name={[name, 'key']} style={{ marginRight: 8 }}>
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
          <Button type="primary" htmlType="submit">
            Save
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default UserVariables;
