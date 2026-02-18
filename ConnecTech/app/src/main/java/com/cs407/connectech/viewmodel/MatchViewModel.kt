// MatchViewModel.kt
package com.cs407.connectech.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.cs407.connectech.model.Match
import com.cs407.connectech.repository.FakeMatchRepository

class MatchViewModel(private val fakeMatchRepository: FakeMatchRepository) : ViewModel() {

    private val _bestMatches = MutableLiveData<List<Match>>()
    val bestMatches: LiveData<List<Match>> get() = _bestMatches

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> get() = _error

    fun fetchBestMatches(tag: String, category: String) {
        try {
            val matches = fakeMatchRepository.getBestMatches(tag, category)
            _bestMatches.value = matches
        } catch (e: Exception) {
            _error.value = e.message
        }
    }
}