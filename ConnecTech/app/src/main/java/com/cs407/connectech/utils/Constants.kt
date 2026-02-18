//Description: This file contains global constants used across the app, such as API endpoints and error messages.
//
//Variables:
//BASE_URL: The base URL for API calls (String).
//API_TIMEOUT: Timeout duration for network requests (Long).
//ERROR_NETWORK: Error message for network failures (String).
//ERROR_UNAUTHORIZED: Error message for unauthorized access (String).
//PREF_USER_SESSION: SharedPreferences key for storing user session data (String).
//PREF_AUTH_TOKEN: SharedPreferences key for storing authentication token (String).

//How to Use: Developers implementing network APIs or handling errors can reference these constants to maintain consistency.


package com.cs407.connectech.utils

object Constants {
    const val BASE_URL = "https://api.connectech.com"
    const val API_TIMEOUT = 30L // Timeout duration in seconds

    // Error Messages
    const val ERROR_NETWORK = "Network error occurred. Please try again."
    const val ERROR_UNAUTHORIZED = "Unauthorized access. Please log in again."

    // SharedPreferences keys
    const val PREF_USER_SESSION = "user_session"
    const val PREF_AUTH_TOKEN = "auth_token"
}
