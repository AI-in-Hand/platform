import React, {useState} from 'react';
import {Button, Form, Input, message, Spin, Typography} from "antd";
import {REGEXP_EMAIL} from "../helpers/constants";
import {getAuth, sendSignInLinkToEmail} from "firebase/auth";
import {useDispatch} from "react-redux";
import {SetEmail} from "../store/actions/usersActions";

const Login = () => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    function handleRegister(data: {email: string}) {
        const auth = getAuth();
        sendSignInLinkToEmail (auth, data.email, {handleCodeInApp: true, url: 'https://platform.ainhand.com/sign-in-verify'}).then((res) => {
            dispatch(SetEmail(data.email))
            message.success("Please check your email for your login link");
        }).catch((error) => {
            console.log(error.message)
        });
    }
    return (
        <Spin spinning={loading}>
            <div className={"mt-20 max-w-[450px] m-auto w-full"}>
                <Typography.Title level={3} className={"text-center"}>
                    Sign In
                </Typography.Title>
                <Form name="login-form" onFinish={handleRegister}>
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
                        <Input placeholder="Email" />
                    </Form.Item>
                    <Form.Item>
                        <Button type={'primary'} htmlType="submit">
                            Sign In
                        </Button>
                    </Form.Item>
                </Form>
            </div>
        </Spin>
    );
};

export default Login;
