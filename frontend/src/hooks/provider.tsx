import React, { useState} from "react";
import {
  getLocalStorage,
  setLocalStorage,
} from "../components/utils";
import {navigate} from "gatsby";
import {ResetState} from "../store/actions/usersActions";
import {useDispatch} from "react-redux";

export interface IUser {
  id: string;
  name: string;
  email?: string;
  username?: string;
  avatar_url?: string;
  metadata?: any;
}

export interface AppContextType {
  user: IUser | null;
  setUser: any;
  cookie_name: string;
  darkMode: string;
  setDarkMode: any;
}

const cookie_name = "coral_app_cookie_";

export const appContext = React.createContext<AppContextType>(
  {} as AppContextType
);
const Provider = ({ children }: any) => {
  const storedValue = getLocalStorage("darkmode", false);
  const [darkMode, setDarkMode] = useState(
    storedValue === null ? "light" : storedValue === "dark" ? "dark" : "light"
  );
  const updateDarkMode = (darkMode: string) => {
    setDarkMode(darkMode);
    setLocalStorage("darkmode", darkMode, false);
  };

  // Modify logic here to add your own authentication
  const initUser = {
    id: "guestuser",
    name: "Guest User",
    email: "guestuser@gmail.com",
    username: "guestuser",
  };
  const [user, setUser] = useState<IUser | null>(initUser);
  return (
    <appContext.Provider
      value={{
        user,
        setUser,
        cookie_name,
        darkMode,
        setDarkMode: updateDarkMode,
      }}
    >
      {children}
    </appContext.Provider>
  );
};

export default ({ element }: any) => <Provider>{element}</Provider>;
