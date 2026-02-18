// MatchViewModelFactory.kt
package com.cs407.connectech.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.cs407.connectech.repository.FakeMatchRepository

class MatchViewModelFactory(private val repository: FakeMatchRepository) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(MatchViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return MatchViewModel(repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}