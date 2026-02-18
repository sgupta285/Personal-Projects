package com.cs407.connectech.network.requests

data class SubmitProblemRequest(
    val problemDetails: String,
    val category: String
)