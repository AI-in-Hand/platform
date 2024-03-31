import React, { useState } from "react";
import { getLocalStorage, setLocalStorage } from "../components/utils";

export interface AppContextType {
  darkMode: string;
  setDarkMode: (mode: string) => void;
}

export const appContext = React.createContext<AppContextType>(
  {} as AppContextType
);

const Provider = ({ children }: any) => {
  const storedValue = getLocalStorage("darkmode", false);
  const [darkMode, setDarkMode] = useState(
    storedValue === null ? "light" : storedValue === "dark" ? "dark" : "light"
  );

  const updateDarkMode = (mode: string) => {
    setDarkMode(mode);
    setLocalStorage("darkmode", mode, false);
  };

  return (
    <appContext.Provider
      value={{
        darkMode,
        setDarkMode: updateDarkMode,
      }}
    >
      {children}
    </appContext.Provider>
  );
};

export default ({ element }: any) => <Provider>{element}</Provider>;
