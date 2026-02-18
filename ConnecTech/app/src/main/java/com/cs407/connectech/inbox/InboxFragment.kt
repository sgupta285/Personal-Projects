package com.cs407.connectech.inbox

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import com.cs407.connectech.databinding.FragmentInboxBinding
import com.cs407.connectech.repository.FakeMatchRepository

class InboxFragment : Fragment() {
    private var _binding: FragmentInboxBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentInboxBinding.inflate(inflater, container, false)
        setupMessages()
        return binding.root
    }

    private fun setupMessages() {
        val args = InboxFragmentArgs.fromBundle(requireArguments())
        val problemDetails = args.problemDetails
        val category = args.category
        val selectedTags = args.selectedTags
        val companyIds = args.companyIds

        val repository = FakeMatchRepository(requireContext())
        val companies = repository.getAllCompanies()

        // Map company IDs to messages
        val messages = companyIds.toList().mapNotNull { companyId ->
            val company = companies.find { it.ranking == companyId }
            company?.let {
                Message(
                    companyName = it.name,
                    problemDescription = problemDetails,
                    tags = listOf(category) + selectedTags
                )
            }
        }

        binding.inboxRecyclerView.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = InboxAdapter(messages) { message ->
                // Handle "Notify" button click for a specific message
                notifyCompany(message)
            }
        }
        // Update UI with problem details, category, and selected tags
        binding.tvProblemDetails.text = problemDetails
        binding.tvCategory.text = category
        binding.tvSelectedTags.text = selectedTags.toString()
    }


    private fun notifyCompany(message: Message) {
        // Logic to notify the company
        Toast.makeText(requireContext(), "Notify clicked for ${message.companyName}", Toast.LENGTH_SHORT).show()
    }


    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
