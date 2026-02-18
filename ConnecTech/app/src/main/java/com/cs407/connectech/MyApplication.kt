// File: MyApplication.kt
package com.cs407.connectech

import android.app.Application
import androidx.room.Room
import com.cs407.connectech.data.AppDatabase

class MyApplication : Application() {
    val database: AppDatabase by lazy {
        Room.databaseBuilder(
            this,
            AppDatabase::class.java,
            "app_db"
        )
            // Remove fallbackToDestructiveMigration to prevent data loss
            .addMigrations(AppDatabase.MIGRATION_1_2) // Use migration defined in AppDatabase
            .build()
    }
}
