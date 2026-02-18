package com.cs407.connectech.inbox

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.cs407.connectech.R

class InboxAdapter(
    private val messages: List<Message>,
    private val onNotifyClicked: (Message) -> Unit // Add click listener as a parameter
) : RecyclerView.Adapter<InboxAdapter.InboxViewHolder>() {

    class InboxViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvCompanyName: TextView = view.findViewById(R.id.tvCompanyName)
        val tvProblemDescription: TextView = view.findViewById(R.id.tvProblemDescription)
        val tvTags: TextView = view.findViewById(R.id.tvTags)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): InboxViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_message, parent, false)
        return InboxViewHolder(view)
    }

    override fun onBindViewHolder(holder: InboxViewHolder, position: Int) {
        val message = messages[position]
        holder.tvCompanyName.text = message.companyName
        holder.tvProblemDescription.text = message.problemDescription
        holder.tvTags.text = message.tags.joinToString(", ")

        // Set click listener for the entire item or a specific button (if needed)
        holder.itemView.setOnClickListener {
            onNotifyClicked(message) // Call the click listener with the current message
        }
    }

    override fun getItemCount(): Int = messages.size
}
