package com.connectech.app

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

/**
 * ProblemViewModel: Manages state and logic for project matching.
 *
 * Variables:
 * - _projects: Internal MutableLiveData holding a list of project names.
 * - projects: Public LiveData exposing project data for observing in UI components.
 * - _matches: Internal MutableLiveData holding a list of matching results for a project.
 * - matches: Public LiveData exposing matches for observing in UI components.
 */
class ProblemViewModel : ViewModel() {

    private val _projects = MutableLiveData<List<String>>() // Internal project data
    val projects: LiveData<List<String>> get() = _projects // Publicly observable projects

    private val _matches = MutableLiveData<List<String>>() // Internal matching results
    val matches: LiveData<List<String>> get() = _matches // Publicly observable matches

    // Fetch projects
    fun fetchProjects() {
        _projects.value = listOf("Project A", "Project B", "Project C") // Mock data
    }

    // Find matches for a project
    fun findMatches(projectId: String) {
        _matches.value = listOf("Tech Partner 1", "Tech Partner 2") // Mock data
    }
}
