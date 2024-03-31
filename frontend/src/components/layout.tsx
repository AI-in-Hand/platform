import * as React from "react";
import { appContext } from "../hooks/provider";
import {Provider} from "react-redux";

/// import ant css
import "antd/dist/reset.css";
import persistor, {store} from "../store";
import {PersistGate} from "redux-persist/integration/react";
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
