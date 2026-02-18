package com.connectech.app

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/**
 * MainViewModel: Manages app-wide states such as user authentication.
 *
 * Variables:
 * - _isUserLoggedIn: Internal MutableLiveData that holds whether the user is logged in.
 * - isUserLoggedIn: Public LiveData exposing the login state for observing in UI components.
 */
class MainViewModel : ViewModel() {

    private val _isUserLoggedIn = MutableLiveData<Boolean>() // Internal login state
    val isUserLoggedIn: LiveData<Boolean> get() = _isUserLoggedIn // Publicly observable login state

    // Function to update login state
    fun updateLoginState(isLoggedIn: Boolean) {
        _isUserLoggedIn.value = isLoggedIn
    }
}
