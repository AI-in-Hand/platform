import React, { useState, useEffect } from "react";
import { Form, Input, Checkbox, Button, message, Tooltip } from "antd";
import { LockOutlined } from "@ant-design/icons";
import { fetchJSON, getServerUrl } from "../../api_utils";
import { useSelector } from "react-redux";

const ProfilePage = ({ data }: any) => {
  const { email } = useSelector((state) => state.user);
  const [form] = Form.useForm();
  const [loading, setLoading] = React.useState(false);
  const [hasValueChange, setHasValueChange] = React.useState(false);
  const [userData, setUserData] = useState<{ [key: string]: string }>({});
  const [initialValues, setInitialValues] = useState<any>({});
  const serverUrl = getServerUrl();
  const userDataUrl = `${serverUrl}/user/profile`;

  useEffect(() => {
    fetchUserData();
  }, []);

  useEffect(() => {
    if (userData) {
      const values = {
        firstName: userData.first_name,
        lastName: userData.last_name,
      };
      form.setFieldsValue(values);
      setInitialValues(values);
    }
  }, [userData, form]);

  const fetchUserData = () => {
    const payLoad = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    };
    const onSuccess = (data: any) => {
      if (data && data.status) {
        setUserData(data?.data);
      } else {
        message.error(data.message);
      }
    };
    const onError = (err: any) => {
      message.error(err.message);
    };
    fetchJSON(userDataUrl, payLoad, onSuccess, onError);
  };

  const handleFinish = (values: any) => {
    setLoading(true);
    const updatedData: { first_name: string; last_name: string } = {
      first_name: values.firstName,
      last_name: values.lastName,
    };
    const payLoad = {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(updatedData),
    };
    const onSuccess = (data: any) => {
      if (data && data.status) {
        message.success(data.message);
        setUserData(data?.data);
      } else {
        message.error(data.message);
      }
      setLoading(false);
    };
    const onError = (err: any) => {
      message.error(err.message);
      setLoading(false);
    };
    fetchJSON(userDataUrl, payLoad, onSuccess, onError);

    // if (values.notifications) {
    //   const AUDIENCE_ID = process.env.MAILCHIMP_AUDIENCE_ID;
    //   const API_KEY = process.env.MAILCHIMP_API_KEY;
    //   const DATACENTER = process.env.MAILCHIMP_API_SERVER;

    //   const url = `https://${DATACENTER}.api.mailchimp.com/3.0/lists/${AUDIENCE_ID}/members`;
    //   const data = {
    //     email_address: values.email,
    //     status: "subscribed",
    //     merge_fields: {
    //       FNAME: values.firstName,
    //       LNAME: values.lastName,
    //     },
    //   };

    //   setLoading(true);

    //   try {
    //     const response = await fetch(url, {
    //       method: "POST",
    //       headers: {
    //         Authorization: `apikey ${API_KEY}`,
    //         "Content-Type": "application/json",
    //       },
    //       body: JSON.stringify(data),
    //     });

    //     const responseData = await response.json();
    //     console.log(responseData, "responseData");
    //     if (response.ok) {
    //       console.log("Successfully subscribed to Mailchimp");
    //     } else {
    //       console.error("Failed to subscribe to Mailchimp", responseData);
    //     }
    //   } catch (error) {
    //     console.error("Error subscribing to Mailchimp", error);
    //   } finally {
    //     setLoading(false);
    //   }
    // }
  };

  const hasChanges = () => {
    const currentValues = form.getFieldsValue();
    if (
      currentValues.firstName.trim() !== initialValues.firstName ||
      currentValues.lastName.trim() !== initialValues.lastName
    ) {
      setHasValueChange(true);
    } else {
      setHasValueChange(false);
    }
  };

  return (
    <div className="flex justify-center items-center">
      <div className="w-full ">
        <h1 className="text-3xl font-bold mb-8">Profile</h1>
        <Form
          form={form}
          onFinish={handleFinish}
          layout="vertical"
          className="space-y-6"
          labelAlign="left"
          onValuesChange={hasChanges}>
          <div className="grid grid-cols-12 gap-4">
            <Form.Item
              label="First Name"
              name="firstName"
              rules={[
                { required: true, message: "Please type your first name!" },
              ]}
              className="col-span-12 sm:col-span-6 mb-4">
              <Input className="rounded-md" />
            </Form.Item>
            <Form.Item
              label="Last Name"
              name="lastName"
              rules={[
                { required: true, message: "Please type your last name!" },
              ]}
              className="col-span-12 sm:col-span-6 mb-4">
              <Input className="rounded-md" />
            </Form.Item>
          </div>
          <Form.Item
            label="Email"
            name="email"
            initialValue={email}
            className="mb-4">
            <Input
              className="rounded-md"
              readOnly
              disabled
              suffix={<LockOutlined />}
            />
          </Form.Item>
          <Form.Item
            name="notifications"
            valuePropName="checked"
            className="mb-4">
            <Checkbox>Subscribe to Mailchimp notifications</Checkbox>
          </Form.Item>
          <Form.Item className="flex">
            <Button
              type="primary"
              htmlType="submit"
              className="rounded-md px-8"
              disabled={!hasValueChange || loading}>
              Save
            </Button>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
};

export default ProfilePage;
