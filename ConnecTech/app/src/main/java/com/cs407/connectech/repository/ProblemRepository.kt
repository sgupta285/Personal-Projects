package com.connectech.app.repository

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData

/**
 * ProblemRepository: Manages project data and operations.
 *
 * Variables:
 * - _projects: Internal MutableLiveData holding a list of projects.
 * - projects: Public LiveData exposing project data for observing in ViewModels.
 * - mockProjects: A mock dataset containing predefined project names.
 */
class ProblemRepository {

    private val _projects = MutableLiveData<List<String>>() // Tracks list of projects
    val projects: LiveData<List<String>> get() = _projects // Public observer for project data

    // Mock project data
    private val mockProjects = listOf("Project A", "Project B", "Project C")

    /**
     * Fetches the list of projects.
     */
    fun fetchProjects() {
        _projects.value = mockProjects
    }

    /**
     * Adds a new project (mock example).
     * @param projectName The name of the new project.
     */
    fun addProject(projectName: String) {
        val updatedProjects = _projects.value?.toMutableList() ?: mutableListOf()
        updatedProjects.add(projectName)
        _projects.value = updatedProjects
    }
}

