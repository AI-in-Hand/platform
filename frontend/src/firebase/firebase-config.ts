import { FirebaseOptions, initializeApp, getApps, getApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Update the firebaseConfig.json file with your app's Firebase project configuration
const config: FirebaseOptions = require("./firebaseConfig.json");

const app = getApps().length ? getApp() : initializeApp(config);
const auth = getAuth(app);

export { auth };
