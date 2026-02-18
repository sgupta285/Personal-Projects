package com.cs407.connectech.model

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "users")
data class User(
    @PrimaryKey val email: String,
    val name: String,
    val password: String,
    val role: String = "user",
    val rating: Float? = null,
    var is_logged_in: Boolean = false
)
