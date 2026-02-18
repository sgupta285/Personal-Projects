package com.cs407.connectech.inbox

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.cs407.connectech.databinding.ItemPaginationBinding

class PaginationAdapter(
    private val pageCount: Int,
    private val onPageClick: (Int) -> Unit
) : RecyclerView.Adapter<PaginationAdapter.PaginationViewHolder>() {

    private var selectedPage: Int = 1

    inner class PaginationViewHolder(private val binding: ItemPaginationBinding) :
        RecyclerView.ViewHolder(binding.root) {
        fun bind(page: Int) {
            binding.pageNumber.text = page.toString()
            binding.pageNumber.isSelected = page == selectedPage

            // Handle clicks
            binding.root.setOnClickListener {
                onPageClick(page)
                selectedPage = page
                notifyDataSetChanged()
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): PaginationViewHolder {
        val inflater = LayoutInflater.from(parent.context)
        val binding = ItemPaginationBinding.inflate(inflater, parent, false)
        return PaginationViewHolder(binding)
    }

    override fun onBindViewHolder(holder: PaginationViewHolder, position: Int) {
        holder.bind(position + 1)
    }

    override fun getItemCount(): Int = pageCount
}
