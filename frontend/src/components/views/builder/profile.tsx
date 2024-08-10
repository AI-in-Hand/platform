import React, { useState, useEffect } from "react";
import { Form, Input, Checkbox, Button, message, Tooltip } from "antd";
import { LockOutlined } from "@ant-design/icons";
import { fetchJSON, getServerUrl } from "../../api_utils";
import { useSelector } from "react-redux";
import { BounceLoader, LoadingOverlay } from "../../atoms";

const ProfilePage = ({ data }: any) => {
  const { email } = useSelector((state) => state.user);
  const [form] = Form.useForm();
  const [loading, setLoading] = React.useState(false);
  const [showFromloading, setShowFromloading] = React.useState(true);
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
        notifications:
          userData.email_subscription === "subscribed" ? true : false,
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
      setShowFromloading(false)
    };
    const onError = (err: any) => {
      message.error(err.message);
      setShowFromloading(false)
    };
    fetchJSON(userDataUrl, payLoad, onSuccess, onError);
  };

  const handleFinish = (values: any) => {
    let sendingNotificationsValue;
    let notificationsValue =
      values.notifications === initialValues.notifications ? false : true;
    if (notificationsValue === true) {
      sendingNotificationsValue =
        values.notifications === true ? "subscribed" : "unsubscribed";
    } else {
      sendingNotificationsValue = "";
    }
    setLoading(true);
    const updatedData: {
      first_name: string;
      last_name: string;
      email_subscription: string;
    } = {
      first_name: values.firstName,
      last_name: values.lastName,
      email_subscription: sendingNotificationsValue,
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
      setHasValueChange(false);
    };
    const onError = (err: any) => {
      message.error(err.message);
      setLoading(false);
      setHasValueChange(false);
    };
    fetchJSON(userDataUrl, payLoad, onSuccess, onError);
  };

  const hasChanges = () => {
    const currentValues = form.getFieldsValue();
    if (
      currentValues?.firstName.trim() !== initialValues.firstName ||
      currentValues?.lastName.trim() !== initialValues.lastName ||
      currentValues?.notifications !== initialValues.notifications
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
        {showFromloading ? (
          <div className="w-full relative">
            <LoadingOverlay loading={showFromloading} />
          </div>
        ) : (
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
              {initialValues.notifications == true ? (
                <Checkbox>Unsubscribe from mailing list</Checkbox>
              ) : (
                <Checkbox>Subscribe to our mailing list</Checkbox>
              )}
            </Form.Item>
            <Form.Item className="flex">
              <Button
                type="primary"
                htmlType="submit"
                className={`${
                  !hasValueChange || loading ? "disable" : ""
                } rounded-md px-8 custom-profile-btn`}
                disabled={!hasValueChange || loading}>
                Save
              </Button>
            </Form.Item>
            {loading && (
            <div className="  w-full text-center">
              {" "}
              <BounceLoader />{" "}
              <span className="inline-block"> loading .. </span>
            </div>
          )}
          </Form>
        )}
      </div>
    </div>
  );
};

export default ProfilePage;
