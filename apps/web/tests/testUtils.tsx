'use client';

import { ReactElement } from "react";
import { render } from "@testing-library/react";
import type { User } from "firebase/auth";
import { vi } from "vitest";

import { AuthContext } from "../components/AuthProvider";

type RenderWithAuthOptions = {
  token?: string | null;
  user?: User | null;
};

const defaultUser = {
  uid: "test-user",
  email: "tester@example.com",
  displayName: "Test User"
} as unknown as User;

export function renderWithAuth(ui: ReactElement, options: RenderWithAuthOptions = {}) {
  const { token = "test-token", user = defaultUser } = options;

  return render(
    <AuthContext.Provider
      value={{
        user,
        token,
        loading: false,
        signInWithGoogle: vi.fn(),
        signOutFromFirebase: vi.fn(),
        getFreshToken: vi.fn().mockResolvedValue(token)
      }}
    >
      {ui}
    </AuthContext.Provider>
  );
}
