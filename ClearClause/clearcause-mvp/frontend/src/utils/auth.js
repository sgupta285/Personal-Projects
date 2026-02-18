/**
 * ClearCause Auth Module
 * Handles user authentication via Amazon Cognito.
 */
import {
  CognitoUserPool,
  CognitoUser,
  AuthenticationDetails,
  CognitoUserAttribute,
} from "amazon-cognito-identity-js";

const POOL_ID = import.meta.env.VITE_COGNITO_USER_POOL_ID;
const CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID;

const userPool = new CognitoUserPool({
  UserPoolId: POOL_ID,
  ClientId: CLIENT_ID,
});

/**
 * Sign up a new user with email and password.
 */
export async function signUp(email, password) {
  const attributes = [
    new CognitoUserAttribute({ Name: "email", Value: email }),
  ];

  return new Promise((resolve, reject) => {
    userPool.signUp(email, password, attributes, null, (err, result) => {
      if (err) return reject(err);
      resolve(result.user);
    });
  });
}

/**
 * Confirm a new user's email with the verification code.
 */
export async function confirmSignUp(email, code) {
  const user = new CognitoUser({ Username: email, Pool: userPool });

  return new Promise((resolve, reject) => {
    user.confirmRegistration(code, true, (err, result) => {
      if (err) return reject(err);
      resolve(result);
    });
  });
}

/**
 * Sign in with email and password. Returns JWT tokens.
 */
export async function signIn(email, password) {
  const user = new CognitoUser({ Username: email, Pool: userPool });
  const authDetails = new AuthenticationDetails({
    Username: email,
    Password: password,
  });

  return new Promise((resolve, reject) => {
    user.authenticateUser(authDetails, {
      onSuccess: (session) => {
        resolve({
          idToken: session.getIdToken().getJwtToken(),
          accessToken: session.getAccessToken().getJwtToken(),
          refreshToken: session.getRefreshToken().getToken(),
        });
      },
      onFailure: (err) => reject(err),
    });
  });
}

/**
 * Sign out the current user.
 */
export function signOut() {
  const user = userPool.getCurrentUser();
  if (user) user.signOut();
}

/**
 * Get the current authenticated user's JWT token, refreshing if needed.
 */
export async function getCurrentToken() {
  const user = userPool.getCurrentUser();
  if (!user) return null;

  return new Promise((resolve, reject) => {
    user.getSession((err, session) => {
      if (err || !session?.isValid()) return resolve(null);
      resolve(session.getIdToken().getJwtToken());
    });
  });
}

/**
 * Check if user is currently authenticated.
 */
export function isAuthenticated() {
  const user = userPool.getCurrentUser();
  return !!user;
}
