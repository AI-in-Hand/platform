import * as React from "react";
import { appContext } from "../hooks/provider";
import {Provider} from "react-redux";

/// import ant css
import "antd/dist/reset.css";
import persistor, {store} from "../store";
import {PersistGate} from "redux-persist/integration/react";
import {initializeApp} from "firebase/app";
import MainLayouts from "../layouts/mainLayouts";

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
  const firebaseConfig = {
    apiKey: "AIzaSyCWIQCLyRF5FD5uQdE4M9l-EDN-NnP09Yg",
     authDomain: "ai-in-hand.firebaseapp.com",
     projectId: "ai-in-hand",
     storageBucket: "ai-in-hand.appspot.com",
     messagingSenderId: "86070783905",
     appId: "1:86070783905:web:2b9eed73fcf06902b7a5e0",
     measurementId: "G-D74MR0JLD5"
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
          <MainLayouts data={{restricted, showHeader, children, link, title, meta}}/>
        </PersistGate>
      </Provider>
  );
};

export default Layout;
