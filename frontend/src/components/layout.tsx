import * as React from "react";
import Header from "./header";
import { appContext } from "../hooks/provider";
import Footer from "./footer";
import {Provider} from "react-redux";

/// import ant css
import "antd/dist/reset.css";
import persistor, {store} from "../store";
import {PersistGate} from "redux-persist/integration/react";
import {initializeApp} from "firebase/app";

type Props = {
  title: string;
  link: string;
  children?: React.ReactNode;
  showHeader?: boolean;
  restricted?: boolean;
  meta?: any;
};

const Layout = ({
  meta,
  title,
  link,
  children,
  showHeader = true,
  restricted = false,
}: Props) => {
  const layoutContent = (
    <div className={`  h-full flex flex-col`}>
      {showHeader && <Header meta={meta} link={link} />}
      <div className="flex-1  text-primary ">
        <title>{meta?.title + " | " + title}</title>
        <div className="   h-full  text-primary">{children}</div>
      </div>
      <Footer />
    </div>
  );
  const firebaseConfig = {
    apiKey: "AIzaSyBAfsvQ8esXSJNWKU-37DsTG_JFDMLRIHs",
    authDomain: "test-8fb59.firebaseapp.com",
    projectId: "test-8fb59",
    storageBucket: "test-8fb59.appspot.com",
    messagingSenderId: "831053501821",
    appId: "1:831053501821:web:70c136fca45ff02e982814"
  };
  initializeApp(firebaseConfig);
  const { darkMode } = React.useContext(appContext);
  React.useEffect(() => {
    document.getElementsByTagName("html")[0].className = `${
      darkMode === "dark" ? "dark bg-primary" : "light bg-primary"
    } `;
  }, [darkMode]);

  return (
      <Provider store={store}>
        <PersistGate persistor={persistor}>
          <appContext.Consumer>
                {(context: any) => {
                  if (restricted) {
                    return <div className="h-full ">{context.user && layoutContent}</div>;
                  } else {
                    return layoutContent;
                  }
                }}
          </appContext.Consumer>
        </PersistGate>
      </Provider>
  );
};

export default Layout;
