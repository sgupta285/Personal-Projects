package com.cs407.connectech.auth

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

class SuccessMessageViewModel : ViewModel() {

    private val _successMessage = MutableLiveData<String>()
    val successMessage: LiveData<String> get() = _successMessage

    fun updateMessage(message: String) {
        _successMessage.value = message
    }
}
