import { combineReducers } from "redux";
import { persistReducer } from "redux-persist";
import storage from "redux-persist/lib/storage";
import user from "./userReducer";

const rootPersistConfig = {
  key: "root",
  storage,
  whitelist: ["user"],
};

const rootReducer = combineReducers({
  user,
});

// @ts-ignore
export default persistReducer(rootPersistConfig, rootReducer);
