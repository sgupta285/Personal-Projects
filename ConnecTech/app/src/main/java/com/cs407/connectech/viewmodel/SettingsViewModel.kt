package com.connectech.app

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

/**
 * SettingsViewModel: Manages user preferences and app settings.
 *
 * Variables:
 * - _preferences: Internal MutableLiveData holding a map of user preferences.
 * - preferences: Public LiveData exposing preferences for observing in UI components.
 */
class SettingsViewModel : ViewModel() {

    private val _preferences = MutableLiveData<Map<String, Any>>() // Internal user preferences
    val preferences: LiveData<Map<String, Any>> get() = _preferences // Publicly observable preferences

    // Update user preference
    fun updatePreference(key: String, value: Any) {
        val updatedPreferences = _preferences.value?.toMutableMap() ?: mutableMapOf()
        updatedPreferences[key] = value
        _preferences.value = updatedPreferences
    }
}
