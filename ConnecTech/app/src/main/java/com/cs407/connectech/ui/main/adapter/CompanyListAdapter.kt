package com.cs407.connectech.ui.main.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import com.cs407.connectech.databinding.ItemCompanyListBinding
import com.cs407.connectech.model.Match

class CompanyListAdapter(
    private val onDeleteClicked: (Match) -> Unit,
    private val onNotifyClicked: (Match) -> Unit
) : ListAdapter<Match, CompanyListAdapter.CompanyListViewHolder>(MatchDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CompanyListViewHolder {
        val binding = ItemCompanyListBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return CompanyListViewHolder(binding)
    }

    override fun onBindViewHolder(holder: CompanyListViewHolder, position: Int) {
        val company = getItem(position)
        holder.bind(company)
    }

    inner class CompanyListViewHolder(private val binding: ItemCompanyListBinding) :
        androidx.recyclerview.widget.RecyclerView.ViewHolder(binding.root) {

        fun bind(match: Match) {
            binding.matchName.text = "Name: ${match.name}"
            binding.matchRating.text = "Ranking: ${match.ranking}"
            binding.matchCategory.text = "Category: ${match.industry}"
            binding.matchLocation.text = "Location: ${match.country}"
            binding.matchSector.text = "Sector: ${match.sector}"
            binding.matchMarketCap.text = "Market Cap: ${match.marketCap}"
            binding.matchStockSymbol.text = "Stock Symbol: ${match.stockSymbol}"

            binding.deleteButton.setOnClickListener {
                onDeleteClicked(match)
            }

            binding.notifyButton.setOnClickListener {
                onNotifyClicked(match)
            }
        }
    }

    class MatchDiffCallback : DiffUtil.ItemCallback<Match>() {
        override fun areItemsTheSame(oldItem: Match, newItem: Match): Boolean {
            return oldItem.ranking == newItem.ranking && oldItem.name == newItem.name
        }

        override fun areContentsTheSame(oldItem: Match, newItem: Match): Boolean {
            return oldItem == newItem
        }
    }
}
