package com.cs407.connectech.data

import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase
import com.cs407.connectech.model.Converters
import com.cs407.connectech.model.User

@Database(entities = [User::class], version = 2, exportSchema = false) // Incremented version to 2
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        // Migration from version 1 to version 2: Add 'is_logged_in' column to 'users' table
        val MIGRATION_1_2 = object : Migration(1, 2) {
            override fun migrate(database: SupportSQLiteDatabase) {
                database.execSQL("ALTER TABLE users ADD COLUMN is_logged_in INTEGER NOT NULL DEFAULT 0")
            }
        }
    }
}
