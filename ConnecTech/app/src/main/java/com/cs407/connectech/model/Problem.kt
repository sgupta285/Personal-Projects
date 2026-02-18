//Description: This file defines the structure for the Problem entity.
// It is used to store and manage the details of problems submitted by users, including metadata such as category and status.
//
//Variables:
// id: Unique identifier for the problem (String).
// title: Short title describing the problem (String).
// description: Detailed description of the problem (String).
// category: Category of the problem (e.g., "AI/ML", "Mobile App Development") (String).
// userId: ID of the user who submitted the problem (String).
// createdAt: Timestamp when the problem was created (ISO 8601 format) (String).
// status: Current status of the problem (e.g., "Pending", "Accepted", "Completed") (String).

// How to Use: Backend developers can map these fields to the database.
// Frontend developers can use this model to display problem details on the Problem Submission Screen and track statuses on the dashboard.
//

package com.cs407.connectech.model

data class Problem(
    val id: String,
    val title: String,
    val description: String,
    val category: String, // e.g., "AI/ML", "Mobile App Development"
    val userId: String,
    val createdAt: String, // ISO 8601 format
    val status: String // e.g., "Pending", "Accepted", "Completed"
)
