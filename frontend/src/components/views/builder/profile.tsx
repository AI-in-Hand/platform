import * as React from "react";
import { Form, Input, Checkbox, Button } from "antd";

const ProfilePage = ({ data }: any) => {
  const [form] = Form.useForm();

  const handleFinish = (values: any) => {
    console.log("Form values:", values);
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
          >
            <div className="grid grid-cols-12 gap-4">
              <Form.Item
                label="First Name"
                name="firstName"
                rules={[{ required: true, message: "Please input your first name!" }]}
                className="col-span-12 sm:col-span-6 mb-4"
              >
                <Input className="rounded-md" />
              </Form.Item>
              <Form.Item
                label="Last Name"
                name="lastName"
                rules={[{ required: true, message: "Please input your last name!" }]}
                className="col-span-12 sm:col-span-6 mb-4"
              >
                <Input className="rounded-md" />
              </Form.Item>
            </div>
            <Form.Item
              label="Email"
              name="email"
              rules={[
                { required: true, message: "Please input your email!" },
                { type: 'email', message: "Please enter a valid email address!" }
              ]}
              className="mb-4"
            >
              <Input className="rounded-md" />
            </Form.Item>
            <Form.Item name="notifications" valuePropName="checked" className="mb-4">
              <Checkbox>Subscribe to Mailchimp notifications</Checkbox>
            </Form.Item>
            <Form.Item className="flex">
              <Button type="primary" htmlType="submit" className="rounded-md px-8">
                Save
              </Button>
            </Form.Item>
          </Form>
        </div>
    </div>
  );
};

export default ProfilePage;
