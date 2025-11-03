'use client';

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import {
  GoogleAuthProvider,
  onIdTokenChanged,
  signInWithPopup,
  signOut,
  type User
} from "firebase/auth";

import { getFirebaseAuth } from "../lib/firebaseClient";

type AuthContextValue = {
  user: User | null;
  token: string | null;
  loading: boolean;
  signInWithGoogle: () => Promise<void>;
  signOutFromFirebase: () => Promise<void>;
  getFreshToken: () => Promise<string | null>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const auth = getFirebaseAuth();
    const unsubscribe = onIdTokenChanged(auth, async (firebaseUser) => {
      if (!isMounted) {
        return;
      }
      setUser(firebaseUser);
      if (firebaseUser) {
        const idToken = await firebaseUser.getIdToken();
        setToken(idToken);
      } else {
        setToken(null);
      }
      setLoading(false);
    });

    const refreshInterval = setInterval(async () => {
      const currentUser = auth.currentUser;
      if (currentUser) {
        const refreshed = await currentUser.getIdToken(true);
        if (isMounted) {
          setToken(refreshed);
        }
      }
    }, 10 * 60 * 1000);

    return () => {
      isMounted = false;
      unsubscribe();
      clearInterval(refreshInterval);
    };
  }, []);

  const signInWithGoogle = useCallback(async () => {
    const auth = getFirebaseAuth();
    const provider = new GoogleAuthProvider();
    provider.setCustomParameters({ prompt: "select_account" });
    await signInWithPopup(auth, provider);
  }, []);

  const signOutFromFirebase = useCallback(async () => {
    const auth = getFirebaseAuth();
    await signOut(auth);
  }, []);

  const getFreshToken = useCallback(async () => {
    const auth = getFirebaseAuth();
    if (!auth.currentUser) {
      return null;
    }
    const fresh = await auth.currentUser.getIdToken(true);
    setToken(fresh);
    return fresh;
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      loading,
      signInWithGoogle,
      signOutFromFirebase,
      getFreshToken
    }),
    [user, token, loading, signInWithGoogle, signOutFromFirebase, getFreshToken]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export { AuthContext };
