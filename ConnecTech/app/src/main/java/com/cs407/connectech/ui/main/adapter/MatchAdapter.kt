package com.cs407.connectech.ui.main.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.cs407.connectech.databinding.ItemMatchBinding
import com.cs407.connectech.model.Match

class MatchAdapter(private val onClick: (Match) -> Unit) :
    ListAdapter<Match, MatchAdapter.MatchViewHolder>(MatchDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MatchViewHolder {
        val binding = ItemMatchBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return MatchViewHolder(binding)
    }

    override fun onBindViewHolder(holder: MatchViewHolder, position: Int) {
        val match = getItem(position)
        holder.bind(match)
    }

    inner class MatchViewHolder(private val binding: ItemMatchBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(match: Match) {
            binding.apply {
                matchName.text = "Name: ${match.name}"
                matchRating.text = "Ranking: ${match.ranking}"
                matchCategory.text = "Category: ${match.industry}"
                matchLocation.text = "Location: ${match.country}"
                matchSector.text = "Sector: ${match.sector}"
                matchMarketCap.text = "Market Cap: ${match.marketCap}"
                matchStockSymbol.text = "Stock Symbol: ${match.stockSymbol}"

                // Set click listener
                root.setOnClickListener {
                    onClick(match)
                }
            }
        }
    }

    class MatchDiffCallback : DiffUtil.ItemCallback<Match>() {
        override fun areItemsTheSame(oldItem: Match, newItem: Match): Boolean {
            // Compare items by a unique identifier, such as ranking
            return oldItem.ranking == newItem.ranking
        }

        override fun areContentsTheSame(oldItem: Match, newItem: Match): Boolean {
            // Compare the entire content of the items
            return oldItem == newItem
        }
    }
}
