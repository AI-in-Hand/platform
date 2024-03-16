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
    apiKey: "AIzaSyCIzUJfhUKoAJQ77khEXZQYxlQbI5nmlrE",
    authDomain: "autogentest-5f95c.firebaseapp.com",
    projectId: "autogentest-5f95c",
    storageBucket: "autogentest-5f95c.appspot.com",
    messagingSenderId: "872767628817",
    appId: "1:872767628817:web:47e12642d6abfa6bb373b0"
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
