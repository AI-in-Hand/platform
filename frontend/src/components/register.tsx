import React, {useEffect} from 'react';
import {getAuth, signInWithEmailLink} from "firebase/auth";
import { navigate} from "gatsby";
import {useDispatch, useSelector} from "react-redux";
import {SignIn} from "../store/actions/usersActions";

const LogInVerify = () => {
    const dispatch = useDispatch();
    // @ts-ignore
    const email = useSelector(store => store.user.email);
    function handleLogin(email: string) {
        const auth = getAuth();
        // @ts-ignore
        signInWithEmailLink (auth, email, location.href).then((res) => {
            // @ts-ignore
            dispatch(SignIn({token: res.user.accessToken, user: {email: res.user.email, uid: res.user.uid}}))
            navigate('/')
            console.log(res.user)
        }).catch((error) => {
            console.log(error.message)
        });
    }
    useEffect(() => {
        handleLogin(email);
        console.log(email)
    }, []);
    return null
};

export default LogInVerify;
