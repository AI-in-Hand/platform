import { FirebaseOptions, initializeApp, getApps, getApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Replace the following with your app's Firebase project configuration
const config: FirebaseOptions = {
  apiKey: "AIzaSyCWIQCLyRF5FD5uQdE4M9l-EDN-NnP09Yg",
  authDomain: "ai-in-hand.firebaseapp.com",
  projectId: "ai-in-hand",
  storageBucket: "ai-in-hand.appspot.com",
  messagingSenderId: "86070783905",
  appId: "1:86070783905:web:2b9eed73fcf06902b7a5e0",
  measurementId: "G-D74MR0JLD5"
};

const app = getApps().length ? getApp() : initializeApp(config);
const auth = getAuth(app);

export { auth };
