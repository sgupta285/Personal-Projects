package com.cs407.connectech.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.cs407.connectech.model.User

@Dao
interface UserDao {

    @Insert(onConflict = OnConflictStrategy.FAIL)
    suspend fun insertUser(user: User)

    @Query("SELECT * FROM users WHERE email = :email AND password = :password LIMIT 1")
    suspend fun getUserByCredentials(email: String, password: String): User?

    @Update
    suspend fun updateUser(user: User)

    @Query("SELECT * FROM users WHERE email = :email LIMIT 1")
    suspend fun getUserByEmail(email: String): User?

    @Query("SELECT * FROM users WHERE is_logged_in = 1 LIMIT 1")
    suspend fun getCurrentUser(): User?

    @Query("UPDATE users SET is_logged_in = 0 WHERE is_logged_in = 1")
    suspend fun logoutAllUsers()

    @Query("UPDATE users SET is_logged_in = 1 WHERE email = :email")
    suspend fun setLoggedIn(email: String)

    @Query("DELETE FROM users")
    suspend fun deleteAllUsers()
}
