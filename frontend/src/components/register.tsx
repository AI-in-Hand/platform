import React, {useEffect} from 'react';
import { message } from "antd";
import { signInWithEmailLink } from "firebase/auth";
import { auth } from '../firebase/firebase-config';
import { navigate} from "gatsby";
import {useDispatch, useSelector} from "react-redux";
import {SignIn} from "../store/actions/usersActions";

const LogInVerify = () => {
    const dispatch = useDispatch();
    // @ts-ignore
    const email = useSelector(store => store.user.email);
    function handleLogin(email: string) {
        // @ts-ignore
        signInWithEmailLink(auth, email, location.href)
          .then((res) => {
            // @ts-ignore
            const expiresIn = Date.now() + (60 * 60 - 1) * 1000; // 1 hour from now, minus 1 second
            dispatch(
              SignIn({
                token: res.user.accessToken,
                expiresIn,
                user: { email: res.user.email, uid: res.user.uid },
              })
            );
            navigate('/');
          })
          .catch((error) => {
            console.log(error.message);
            message.error("Error logging in. Please try again.");
          });
    }
    useEffect(() => {
        handleLogin(email);
    }, []);
    return null
};

export default LogInVerify;
