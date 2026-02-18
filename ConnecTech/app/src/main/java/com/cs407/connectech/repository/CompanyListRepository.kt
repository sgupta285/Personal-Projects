package com.cs407.connectech.repository

import com.cs407.connectech.model.Match

object CompanyListRepository {
    private val selectedCompanies = mutableListOf<Match>()

    fun addCompany(company: Match) {
        selectedCompanies.add(company)
    }

    fun removeCompany(company: Match) {
        selectedCompanies.remove(company)
    }

    fun getSelectedCompanies(): List<Match> {
        return selectedCompanies
    }

    fun clear() {
        selectedCompanies.clear()
    }
}
