import * as React from "react";
import { Form, Input, Checkbox, Button } from "antd";

const ProfilePage = ({ data }: any) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = React.useState(false);

  const handleFinish = async (values: any) => {
    
    if (values.notifications) {
      const AUDIENCE_ID = process.env.MAILCHIMP_AUDIENCE_ID;
      const API_KEY = process.env.MAILCHIMP_API_KEY;
      const DATACENTER = process.env.MAILCHIMP_API_SERVER;

      const url = `https://${DATACENTER}.api.mailchimp.com/3.0/lists/${AUDIENCE_ID}/members`;
      const data = {
        email_address: values.email,
        status: "subscribed",
        merge_fields: {
          FNAME: values.firstName,
          LNAME: values.lastName,
        },
      };

      setLoading(true);

      try {
        const response = await fetch(url, {
          method: "POST",
          headers: {
            Authorization: `apikey ${API_KEY}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        });

        const responseData = await response.json();
        console.log(responseData,"responseData");
        if (response.ok) {
          console.log("Successfully subscribed to Mailchimp");
        } else {
          console.error("Failed to subscribe to Mailchimp", responseData);
        }
      } catch (error) {
        console.error("Error subscribing to Mailchimp", error);
      } finally {
        setLoading(false);
      }
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
          labelAlign="left">
          <div className="grid grid-cols-12 gap-4">
            <Form.Item
              label="First Name"
              name="firstName"
              rules={[
                { required: true, message: "Please input your first name!" },
              ]}
              className="col-span-12 sm:col-span-6 mb-4">
              <Input className="rounded-md" />
            </Form.Item>
            <Form.Item
              label="Last Name"
              name="lastName"
              rules={[
                { required: true, message: "Please input your last name!" },
              ]}
              className="col-span-12 sm:col-span-6 mb-4">
              <Input className="rounded-md" />
            </Form.Item>
          </div>
          <Form.Item
            label="Email"
            name="email"
            rules={[
              { required: true, message: "Please input your email!" },
              { type: "email", message: "Please enter a valid email address!" },
            ]}
            className="mb-4">
            <Input className="rounded-md" />
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
              className="rounded-md px-8">
              Save
            </Button>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
};

export default ProfilePage;
