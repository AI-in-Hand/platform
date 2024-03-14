import React, {useState} from 'react';
import {Button, Form, Input, Spin, Typography} from "antd";
import {REGEXP_EMAIL} from "../helpers/constants";
import {Link, navigate} from "gatsby";
import {getAuth, signInWithEmailLink} from "firebase/auth";
import {useDispatch} from "react-redux";
import {SignIn} from "../store/actions/usersActions";

const Login = () => {
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    function handleLogin(data: {email: string, password: string}) {
        const auth = getAuth();
        // @ts-ignore
        signInWithEmailLink (auth, data.email, location.href).then((res) => {
            // @ts-ignore
            dispatch(SignIn({token: res.user.accessToken, user: {email: res.user.email, uid: res.user.uid}}))
            navigate('/')
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
                <Form name="login-form" onFinish={handleLogin}>
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
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                        <Link to="/sign-up">Sign Up</Link>
                    </div>
                </Form>
            </div>
        </Spin>
    );
};

export default Login;
