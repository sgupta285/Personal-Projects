package com.cs407.connectech.model

data class Match(
    val ranking: Int,
    val name: String,
    val marketCap: String,
    val stockSymbol: String,
    val country: String,
    val sector: String,
    val industry: String
)
