import React, {useEffect} from 'react';
import {appContext} from "../hooks/provider";
import Header from "../components/header";
import Footer from "../components/footer";
import {navigate} from "gatsby";
import {useSelector} from "react-redux";
import { useLocation } from "@reach/router"

const MainLayouts = ({data}: any) => {
    // @ts-ignore
    const loggedIn = useSelector(state => state.user.loggedIn);
    const location = useLocation();
    const {restricted, showHeader, children, link, title, meta} = data;
    const layoutContent = (
        <div className={`h-full flex flex-col`}>
            {showHeader && <Header meta={meta} link={link} loggedIn={loggedIn} />}
            <div className="flex-1  text-primary ">
                <title>{meta?.title + " | " + title}</title>
                <div className="h-full text-primary">{children}</div>
            </div>
            <Footer />
        </div>
    );
    useEffect(() => {
        if (location.pathname !== '/sign-in') {
            if (!loggedIn) {
                navigate("/sign-in")
            }
        }
    }, [loggedIn]);
    return (
        <appContext.Consumer>
            {(context: any) => {
                if (restricted) {
                    return <div className="h-full">{loggedIn && layoutContent}</div>;
                } else {
                    return layoutContent;
                }
            }}
        </appContext.Consumer>
    );
};

export default MainLayouts;
