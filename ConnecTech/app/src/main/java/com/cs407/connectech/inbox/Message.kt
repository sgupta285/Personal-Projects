package com.cs407.connectech.inbox

data class Message(
    val companyName: String,
    val problemDescription: String,
    val tags: List<String>
)
