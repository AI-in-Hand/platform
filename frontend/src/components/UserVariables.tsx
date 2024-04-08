import React, { useState, useEffect } from 'react';
import { Form, Input, Button, message, Table } from 'antd';
import { fetchJSON, getServerUrl } from './utils';
import { MinusIcon, PlusIcon } from "@heroicons/react/24/outline";

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
      title: 'Name',
      dataIndex: 'key',
      key: 'key',
    },
    {
      title: 'Value',
      dataIndex: 'value',
      key: 'value',
      render: (_, record: any) => (
        <Form.Item name={record.key}>
          <Input.Password placeholder="***" autoComplete="new-password" />
        </Form.Item>
      ),
    },
    {
      title: '',
      key: 'action',
      render: (_, record: any) => (
        <Button onClick={() => {
          const newSecrets = { ...secrets };
          delete newSecrets[record.key];
          setSecrets(newSecrets);
          form.setFieldsValue({ [record.key]: undefined });
        }}>
          <MinusIcon className="w-5 h-5 inline-block mr-1" />
        </Button>
      ),
    },
  ];

  const data = Object.keys(secrets).map((key) => ({
    key,
    value: secrets[key],
  }));

  return (
    <div className=" text-primary ">
      <section aria-labelledby="note-important">
        <h2 id="note-important">Important Note</h2>
        <p>
          Set the <code>OPENAI_API_KEY</code> variable to use agencies (workflows).
        </p>
      </section>

      <details>
        <summary><strong>Understanding Secrets</strong> (click to expand or hide)</summary>
        <section aria-labelledby="secrets-introduction">
          <h2 id="secrets-introduction">Introduction</h2>
          <p>
            Use secret variables to securely access sensitive data like API keys in your skills. They're encrypted at rest and decrypted only during use.
          </p>
          <p>
            Note: After saving a secret, you can't view its value again. To change a secret, simply update it with a new value.
          </p>
        </section>

        <section aria-labelledby="usage-instructions">
          <h2 id="usage-instructions">Using Secrets in Skills</h2>
          <p>Example usage for a secret named <code>AIRTABLE_TOKEN</code>:</p>
          <pre>
            <code>from backend.services.user_secret_manager import UserSecretManager</code><br />
            <code>user_secret_manager = UserSecretManager(UserSecretStorage())</code><br />
            <code>airtable_token = user_secret_manager.get_by_key("AIRTABLE_TOKEN")</code><br />
          </pre>
        </section>
      </details>

      <section aria-labelledby="secrets-list">
        <h2 id="secrets-list">Your Secrets</h2>
        <p>Here's a list of your secrets. Add new or update existing ones as needed.</p>

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
                      <Input placeholder="Name" />
                    </Form.Item>
                    <Form.Item
                      {...restField}
                      name={[name, 'value']}
                      style={{ width: '50%' }}
                    >
                      <Input.Password placeholder="Value" autoComplete="new-password" />
                    </Form.Item>

                    <Button onClick={() => remove(name)}>
                    <MinusIcon className="w-5 h-5 inline-block mr-1" />
                    </Button>
                  </div>
                ))}
                <Form.Item>
                  <Button type="dashed" onClick={() => add()} block>
                    <PlusIcon className="w-5 h-5 inline-block mr-1" /> Add Secret
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
      </section>
    </div>
  );
};

export default UserVariables;
