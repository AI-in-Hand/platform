import React, {useState} from 'react';
import {getAuth, sendSignInLinkToEmail} from "firebase/auth";
import {Link} from "gatsby";
import {Button, Form, Input, Spin, Typography} from "antd";
import {REGEXP_EMAIL} from "../helpers/constants";

const Register = () => {
    const [loading, setLoading] = useState(false);
    function handleRegister(data: {email: string, password: string}) {
        const auth = getAuth();
        sendSignInLinkToEmail (auth, data.email, {handleCodeInApp: true, url: 'http://localhost:8000/sign-in'}).then((res) => {
            console.log('register success')
        }).catch((error) => {
            console.log(error.message)
        });
    }
    return (
        <Spin spinning={loading}>
            <div className={"mt-20 max-w-[450px] m-auto w-full"}>
                <Typography.Title level={3} className={"text-center"}>
                    Sign Up
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
                            Sign Up
                        </Button>
                    </Form.Item>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                        <Link to="/sign-in">Sign In</Link>
                    </div>
                </Form>
            </div>
        </Spin>
    );
};

export default Register;
