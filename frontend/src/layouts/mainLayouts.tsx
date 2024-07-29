import React, { useEffect } from "react";
import { appContext } from "../hooks/provider";
import Header from "../components/header";
import Footer from "../components/footer";
import Disclaimer from "../components/disclaimer";
import { navigate } from "gatsby";
import { useSelector } from "react-redux";
import { useLocation } from "@reach/router";

const MainLayouts = ({ data }: any) => {
  // @ts-ignore
  const loggedIn = useSelector((state) => state.user.loggedIn);

  const shouldBeInSignInPage = () =>
    !(location.pathname.includes("/sign-in") || loggedIn);
  const shouldNotBeInSignInPage = () =>
    location.pathname.includes("/sign-in") && loggedIn;

  const location = useLocation();
  const { restricted, showHeader, children, link, title, meta } = data;

  const layoutContent = (
    <div className={`h-full flex flex-col`}>
      {showHeader && <Header meta={meta} link={link} loggedIn={loggedIn} />}
      <div className="flex-1  text-primary ">
        <title>{meta?.title + " | " + title}</title>
        <div className="h-full text-primary">{children}</div>
      </div>
      <Footer />
      {loggedIn && (
        <Disclaimer loggedIn={loggedIn} />
      )}
    </div>
  );

  useEffect(() => {
    if (shouldBeInSignInPage()) {
      navigate("/sign-in");
    } else if (shouldNotBeInSignInPage()) {
      navigate("/");
    }
  }, []);

  return (
    <appContext.Consumer>
      {(context: any) => {
        if (shouldBeInSignInPage() || shouldNotBeInSignInPage()) {
          return <></>;
        }
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
