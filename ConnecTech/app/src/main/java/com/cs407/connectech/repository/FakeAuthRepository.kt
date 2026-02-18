package com.cs407.connectech.repository

import androidx.lifecycle.MutableLiveData
import com.cs407.connectech.data.UserDao
import com.cs407.connectech.model.User
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext

class FakeAuthRepository(private val userDao: UserDao) : AuthRepository {

    private var loggedInUserEmail: String? = null

    override suspend fun login(email: String, password: String): Result<User> {
        return withContext(Dispatchers.IO) {
            delay(500)
            val user = userDao.getUserByCredentials(email, password)
            if (user != null) {
                userDao.logoutAllUsers()    // Ensure no other user is logged_in
                userDao.setLoggedIn(user.email) // Mark the current user as logged_in
                loggedInUserEmail = user.email
                Result.success(user)
            } else {
                Result.failure(Exception("Invalid email or password"))
            }
        }
    }


    override suspend fun register(email: String, password: String): Result<User> {
        return withContext(Dispatchers.IO) {
            delay(500)
            if (email.contains("@") && email.contains( ".") && password.length >= 4) {
                val existing = userDao.getUserByEmail(email)
                if (existing != null) {
                    Result.failure(Exception("User already exists"))
                } else {
                    val newUser = User(email = email, name = "New User", password = password)
                    userDao.insertUser(newUser)
                    Result.success(newUser)
                }
            } else {
                Result.failure(Exception("Invalid email or password format"))
            }
        }
    }

    override suspend fun resetPassword(email: String): Result<Void?> {
        return withContext(Dispatchers.IO) {
            delay(500)
            val user = userDao.getUserByEmail(email)
            if (user != null) {
                Result.success(null)
            } else {
                Result.failure(Exception("User not found"))
            }
        }
    }

    override suspend fun submitProblem(problemDetails: String, category: String): Result<Boolean> {
        return withContext(Dispatchers.IO) {
            delay(500)
            if (problemDetails.isNotEmpty() && category.isNotEmpty()) {
                Result.success(true)
            } else {
                Result.failure(Exception("Problem details or category cannot be empty"))
            }
        }
    }

    override suspend fun updatePassword(email: String, newPassword: String): Result<Boolean> {
        return withContext(Dispatchers.IO) {
            val user = userDao.getUserByEmail(email)
            if (user != null) {
                val updatedUser = user.copy(password = newPassword)
                userDao.updateUser(updatedUser)
                Result.success(true)
            } else {
                Result.failure(Exception("User not found"))
            }
        }
    }

    override suspend fun getCurrentUserEmail(): String? {
        return withContext(Dispatchers.IO) {
            val currentUser = userDao.getCurrentUser()
            currentUser?.email
        }
    }



    override fun logout() {
        loggedInUserEmail = null
        // logoutAllUsers is a suspend function, so we need to run this on a background thread.
        // Since logout is a quick action,  making it suspend and calling from ViewModel or
        // use runBlocking just to illustrate.
        runBlocking {
            userDao.logoutAllUsers()
        }
    }


    override fun getLoggedInUser(): String? {
        return loggedInUserEmail
    }
}
