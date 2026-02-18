// FakeMatchRepository.kt
package com.cs407.connectech.repository

import android.content.Context
import com.cs407.connectech.model.Match
import com.opencsv.CSVReaderBuilder
import java.io.InputStreamReader

class FakeMatchRepository(private val context: Context) {

    private val companies: List<Match> by lazy { loadCompanies() }

    private fun loadCompanies(): List<Match> {
        val companies = mutableListOf<Match>()
        val inputStream = context.assets.open("companies.csv")
        val reader = CSVReaderBuilder(InputStreamReader(inputStream))
            .withSkipLines(1) // Skip header line
            .build()

        reader.forEach { line ->
            val ranking = line[0].toIntOrNull() ?: 0
            val name = line[1]
            val marketCap = line[2]
            val stockSymbol = line[3]
            val country = line[4]
            val sector = line[5]
            val industry = line[6]

            val company = Match(
                ranking = ranking,
                name = name,
                marketCap = marketCap,
                stockSymbol = stockSymbol,
                country = country,
                sector = sector,
                industry = industry
            )
            companies.add(company)
        }

        reader.close()
        return companies
    }

    fun getAllCompanies(): List<Match> {
        return companies
    }

    fun getCompanyById(id: Int): Match? {
        return companies.firstOrNull { it.ranking == id }
    }

    fun getBestMatches(tag: String, category: String): List<Match> {
        val categoryMatches = companies.filter { it.industry == tag } // Filter by tag (industry)
        return when (category.lowercase()) { // Sort by category
            "market cap" -> categoryMatches.sortedByDescending { it.marketCap.toLongOrNull() }
            "ranking" -> categoryMatches.sortedBy { it.ranking }
            else -> categoryMatches
        }
    }
}