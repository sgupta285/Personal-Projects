//Description: This file represents a tech provider entity and includes fields like expertise and availability.
//
//Variables:
//id: Unique identifier for the provider (String).
//name: Name of the tech provider (String).
//expertise: List of expertise categories (e.g., "AI/ML", "Web Development") (List<String>).
//rating: Rating of the provider (Float).
//availability: Boolean flag indicating whether the provider is available to take on new projects (Boolean).

//How to Use: The matching algorithm team can use expertise and availability for better matching. Frontend developers can display these details in the Best Matches Screen.

package com.cs407.connectech.model

data class Provider(
    val id: String,
    val name: String,
    val expertise: List<String>, // List of categories e.g., ["AI/ML", "Web Development"]
    val rating: Float,
    val availability: Boolean // Availability status
)
