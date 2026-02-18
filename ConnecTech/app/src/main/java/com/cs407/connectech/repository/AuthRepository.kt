package com.cs407.connectech.repository

import com.cs407.connectech.model.User

/**
 * Interface defining authentication-related data operations.
 */
interface AuthRepository {
    suspend fun login(email: String, password: String): Result<User>
    suspend fun register(email: String, password: String): Result<User>
    suspend fun resetPassword(email: String): Result<Void?>
    suspend fun submitProblem(problemDetails: String, category: String): Result<Boolean>
    fun logout()
    fun getLoggedInUser(): String?
    suspend fun updatePassword(email: String, newPassword: String): Result<Boolean>?
    suspend fun getCurrentUserEmail(): String?
}
