import "@testing-library/jest-dom/vitest";

process.env.NEXT_PUBLIC_FIREBASE_API_KEY ??= "test-api-key";
process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN ??= "test.firebaseapp.com";
process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID ??= "test-project";
process.env.NEXT_PUBLIC_FIREBASE_APP_ID ??= "1:1234567890:web:abcdef123456";
process.env.NEXT_PUBLIC_API_BASE ??= "http://localhost";
