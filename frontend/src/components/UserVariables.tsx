import React, { useState, useEffect } from 'react';
import { Form, Input, Button, message, Table } from 'antd';
import { fetchJSON, getServerUrl } from './utils';

const UserVariables = () => {
  const [form] = Form.useForm();
  const [secrets, setSecrets] = useState<{ [key: string]: string }>({});
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
        const fetchedSecrets = {};
        data.data.forEach((key) => {
          fetchedSecrets[key] = '***';
        });
        setSecrets(fetchedSecrets);
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
    Object.keys(secrets).forEach((key) => {
      if (values[key] !== '***') {
        updatedSecrets[key] = values[key] || '';
      }
    });
    Object.entries(values.newSecrets || {}).forEach(([_, { key, value }]) => {
      if (key) {
        updatedSecrets[key] = value || '';
      }
    });

    const payLoad = {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updatedSecrets),
    };
    const onSuccess = (data: any) => {
      if (data && data.status) {
        message.success(data.message);
        const newSecrets = {};
        data.data.forEach((key) => {
          newSecrets[key] = '***';
        });
        setSecrets(newSecrets);
        form.resetFields();
      } else {
        message.error(data.message);
      }
    };
    const onError = (err: any) => {
      message.error(err.message);
    };
    fetchJSON(getUserSecretsUrl, payLoad, onSuccess, onError);
  };

  const columns = [
    {
      title: 'Secret Name',
      dataIndex: 'key',
      key: 'key',
    },
    {
      title: 'Secret Value',
      dataIndex: 'value',
      key: 'value',
      render: (_, record: any) => (
        <Form.Item name={record.key}>
          <Input.Password placeholder="***" autoComplete="new-password" />
        </Form.Item>
      ),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record: any) => (
        <Button onClick={() => {
          const newSecrets = { ...secrets };
          delete newSecrets[record.key];
          setSecrets(newSecrets);
          form.setFieldsValue({ [record.key]: undefined });
        }}>
          Remove
        </Button>
      ),
    },
  ];

  const data = Object.keys(secrets).map((key) => ({
    key,
    value: secrets[key],
  }));

  return (
    <div>
      <Form form={form} onFinish={saveSecrets}>
        <Table columns={columns} dataSource={data} pagination={false} rowKey="key" />
        <Form.List name="newSecrets">
          {(fields, { add, remove }) => (
            <>
              {fields.map(({ key, name, ...restField }) => (
                <div key={key} style={{ display: 'flex', marginBottom: 8 }}>
                  <Form.Item
                    {...restField}
                    name={[name, 'key']}
                    style={{ marginRight: 8, width: '50%' }}
                  >
                    <Input placeholder="Secret Name" />
                  </Form.Item>
                  <Form.Item
                    {...restField}
                    name={[name, 'value']}
                    style={{ width: '50%' }}
                  >
                    <Input.Password placeholder="Secret Value" autoComplete="new-password" />
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
