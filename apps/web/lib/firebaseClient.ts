'use client';

import { FirebaseOptions, getApp, getApps, initializeApp } from "firebase/app";
import {
  browserLocalPersistence,
  getAuth,
  GoogleAuthProvider,
  setPersistence,
  signInWithPopup,
  signOut,
  onIdTokenChanged,
  User,
  Auth
} from "firebase/auth";

const firebaseConfig: FirebaseOptions = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID
};

function assertConfig(config: FirebaseOptions): asserts config is Required<FirebaseOptions> {
  const requiredKeys: Array<keyof FirebaseOptions> = ["apiKey", "authDomain", "projectId", "appId"];
  const missing = requiredKeys.filter((key) => !config[key]);
  if (missing.length > 0) {
    throw new Error(`Missing Firebase configuration: ${missing.join(", ")}`);
  }
}

let authInstance: Auth | null = null;

export function getFirebaseAuth(): Auth {
  if (authInstance) {
    return authInstance;
  }
  assertConfig(firebaseConfig);
  const app = getApps().length ? getApp() : initializeApp(firebaseConfig);
  const auth = getAuth(app);
  auth.languageCode = "ja";
  setPersistence(auth, browserLocalPersistence).catch((error) => {
    console.warn("Failed to set Firebase persistence", error);
  });
  authInstance = auth;
  return auth;
}

export {
  GoogleAuthProvider,
  signInWithPopup,
  signOut,
  onIdTokenChanged,
  type User
};
