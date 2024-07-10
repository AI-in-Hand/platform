import React, { useState, useEffect } from "react";
import { Form, Input, Button, message, Table, } from "antd";
import { fetchJSON, getServerUrl } from "./api_utils";
import {
  XMarkIcon,
  PlusIcon,
  PencilIcon,
  LockClosedIcon,
} from "@heroicons/react/24/outline";

const UserVariables = () => {
  const [form] = Form.useForm();
  const [variables, setVariables] = useState<{ [key: string]: string }>({});
  const serverUrl = getServerUrl();
  const getUserVariablesUrl = `${serverUrl}/user/settings/variables`;
  const [editingKey, setEditingKey] = useState<string | null>(null);

  useEffect(() => {
    fetchVariables();
  }, []);

  const fetchVariables = () => {
    const payLoad = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    };
    const onSuccess = (data: any) => {
      if (data && data.status) {
        const fetchedVariables = {};
        data.data.forEach((key) => {
          fetchedVariables[key] = "***";
        });
        setVariables(fetchedVariables);
      } else {
        message.error(data.message);
      }
    };
    const onError = (err: any) => {
      message.error(err.message);
    };
    fetchJSON(getUserVariablesUrl, payLoad, onSuccess, onError);
  };

  const saveVariables = (values: any) => {
    const updatedVariables: { [key: string]: string } = {};
    Object.keys(variables).forEach((key) => {
      if (values[key] !== "***") {
        updatedVariables[key] = values[key] || "";
      }
    });
    Object.entries(values.newVariables || {}).forEach(([_, { key, value }]) => {
      if (key) {
        updatedVariables[key] = value || "";
      }
    });

    const payLoad = {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(updatedVariables),
    };
    const onSuccess = (data: any) => {
      if (data && data.status) {
        message.success(data.message);
        const newVariables = {};
        data.data.forEach((key) => {
          newVariables[key] = "***";
        });
        setVariables(newVariables);
        form.resetFields();
        setEditingKey(null);
      } else {
        message.error(data.message);
      }
    };
    const onError = (err: any) => {
      message.error(err.message);
    };
    fetchJSON(getUserVariablesUrl, payLoad, onSuccess, onError);
  };

  const toggleEdit = (key: string) => {
    setEditingKey(editingKey === key ? null : key);
  };

  const columns = [
    {
      title: "Name",
      dataIndex: "key",
      key: "key",
    },
    {
      title: "Value",
      dataIndex: "value",
      key: "value",
      className:"variable-value-wrap",
      render: (_, record: any) => (
        <Form.Item
          name={record.key}>
          <Input.Password placeholder="***" autoComplete="new-password" className={editingKey === record.key ? "" : "hide-variable"}/>
          {editingKey === record.key ? null : (
            <LockClosedIcon className="w-5 h-5 inline-block" />
          )}
        </Form.Item>
      ),
    },
    {
      title: "",
      key: "action",
      className:"variable-button-wrap",
      render: (_, record: any) => (
        <>
          <Button onClick={() => toggleEdit(record.key)} className="mr-2 px-3">
            <PencilIcon className="w-5 h-5 inline-block" />
          </Button>
          <Button
            onClick={() => {
              const newVariables = { ...variables };
              delete newVariables[record.key];
              setVariables(newVariables);
              form.setFieldsValue({ [record.key]: undefined });
            }}
            className="px-3">
            <XMarkIcon className="w-5 h-5 inline-block" />
          </Button>
        </>
      ),
    },
  ];

  const data = Object.keys(variables).map((key) => ({
    key,
    value: variables[key],
  }));

  return (
    <div className=" text-primary ">
      <section aria-labelledby="note-important">
        <h2 id="note-important">Important Note</h2>
        <p>
          Set the <code>OPENAI_API_KEY</code> variable to use OpenAI's API. You
          can find your API key in the{" "}
          <u>
            <a
              href="https://platform.openai.com/api-keys"
              target="_blank"
              rel="noreferrer">
              OpenAI dashboard
            </a>
          </u>
          .
        </p>
      </section>

      <details>
        <summary>
          <strong>Using Azure OpenAI</strong> (click to expand or hide)
        </summary>
        <section>
          <p>
            To use Azure OpenAI, set the following variables:
            AZURE_OPENAI_ENDPOINT (e.g.
            https://example-resource.azure.openai.com/), OPENAI_API_VERSION
            (e.g. 2024-02-15-preview), AZURE_OPENAI_API_KEY.
          </p>
        </section>
      </details>

      <details>
        <summary>
          <strong>Understanding Variables</strong> (click to expand or hide)
        </summary>
        <section aria-labelledby="variables-introduction">
          <h2 id="variables-introduction">Introduction</h2>
          <p>
            Use variables to securely access sensitive data like API keys in
            your skills. They're encrypted at rest and decrypted only during
            use.
          </p>
          <p>
            Note: After saving a variable, you can't view its value again. To
            change it, simply update it with a new value.
          </p>
        </section>

        <section aria-labelledby="usage-instructions">
          <h2 id="usage-instructions">Using Variables in Skills</h2>
          <p>
            Example usage for a variable named <code>AIRTABLE_TOKEN</code>:
          </p>
          <pre>
            <code>
              from backend.services.user_variable_manager import
              UserVariableManager
            </code>
            <br />
            <code>
              user_variable_manager = UserVariableManager(UserVariableStorage())
            </code>
            <br />
            <code>
              airtable_token =
              user_variable_manager.get_by_key("AIRTABLE_TOKEN")
            </code>
            <br />
          </pre>
        </section>
      </details>

      <section aria-labelledby="variables-list">
        <h2 id="variables-list">Your Variables</h2>
        <p>
          Here's a list of your variables. Add new or update existing ones as
          needed.
        </p>

        <Form form={form} onFinish={saveVariables}>
          <Table
            columns={columns}
            dataSource={data}
            pagination={false}
            rowKey="key"
          />
          <Form.List name="newVariables">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => (
                  <div key={key} style={{ display: "flex", marginBottom: 8 }} className="pt-6">
                    <Form.Item
                      {...restField}
                      name={[name, "key"]}
                      style={{ marginRight: 8, width: "50%" }}>
                      <Input placeholder="Name" />
                    </Form.Item>
                    <Form.Item
                      {...restField}
                      name={[name, "value"]}
                      style={{ width: "50%" }}>
                      <Input.Password
                        placeholder="Value"
                        autoComplete="new-password"
                      />
                    </Form.Item>

                    <Button onClick={() => remove(name)} className="ml-2 px-3">
                      <XMarkIcon className="w-5 h-5 inline-block" />
                    </Button>
                  </div>
                ))}
                <Form.Item>
                  <Button type="dashed" onClick={() => add()} block>
                    <PlusIcon className="w-5 h-5 inline-block mr-1" /> Add
                    Variable
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
