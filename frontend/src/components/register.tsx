import React, { useEffect } from "react";
import { message } from "antd";
import { signInWithEmailLink } from "firebase/auth";
import { auth } from '../firebase/firebase-config';
import { navigate} from "gatsby";
import {useDispatch, useSelector} from "react-redux";
import {SignIn} from "../store/actions/usersActions";

const LogInVerify = () => {
    const dispatch = useDispatch();
    const userEmail = useSelector(state => state.user.email);

    function handleLogin(email: string) {
        signInWithEmailLink(auth, email, location.href)
          .then((res) => {
            const expiresIn = Date.now() + (55 * 60) * 1000; // 55 minutes from now
            dispatch(
              SignIn({
                token: res.user.accessToken,
                expiresIn,
                email: res.user.email,
                uid: res.user.uid,
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
        handleLogin(userEmail);
    }, []);
    return null
};

export default LogInVerify;
