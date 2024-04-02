import React, {useState} from "react";
import {Button, Form, Input, message, Spin, Typography} from "antd";
import {REGEXP_EMAIL} from "../helpers/constants";
import { sendSignInLinkToEmail } from "firebase/auth";
import { auth } from '../firebase/firebase-config';
import { useDispatch, useSelector } from "react-redux";
import {SetEmail} from "../store/actions/usersActions";

const Login = () => {
    const dispatch = useDispatch();
    const signInVerifyUrl = `${window.location.origin}/sign-in-verify`;
    const [loading, setLoading] = useState(false);
    const userEmail = useSelector(state => state.user.email);

    function handleRegister(data: {email: string}) {
        setLoading(true);
        sendSignInLinkToEmail(auth, data.email, {handleCodeInApp: true, url: signInVerifyUrl}).then((res) => {
            dispatch(SetEmail(data.email))
            message.success("Please check your email for your login link");
        }).catch((error) => {
            console.log(error.message)
        }).finally(() => {
            setLoading(false);
        });
    }
    return (
        <Spin spinning={loading}>
            <div className={"mt-20 max-w-[350px] m-auto w-full"}>
                <Typography.Title level={3} className={"text-center"}>
                    Sign In / Register
                </Typography.Title>
                <Form name="login-form" onFinish={handleRegister} initialValues={{email: userEmail}}>
                    <Form.Item
                        name="email"
                        rules={[
                            { required: true, message: "Please input your email!" },
                            () => ({
                                validator(_, value) {
                                    if (REGEXP_EMAIL.test(value)) {
                                        return Promise.resolve();
                                    }
                                    return Promise.reject(new Error("Email not valid"));
                                },
                            }),
                        ]}
                    >
                        <Input placeholder="Your Email" type="email" />
                    </Form.Item>
                    <Form.Item className={"text-center"}>
                        <Button type={'primary'} htmlType="submit">
                            Send Login Link
                        </Button>
                    </Form.Item>
                </Form>
            </div>
        </Spin>
    );
};

export default Login;
