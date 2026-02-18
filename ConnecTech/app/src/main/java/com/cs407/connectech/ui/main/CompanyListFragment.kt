package com.cs407.connectech.ui.main

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.cs407.connectech.R
import com.cs407.connectech.databinding.FragmentCompanyListBinding
import com.cs407.connectech.model.Match
import com.cs407.connectech.repository.CompanyListRepository
import com.cs407.connectech.ui.main.adapter.CompanyListAdapter

class CompanyListFragment : Fragment() {

    private var _binding: FragmentCompanyListBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(inflater: LayoutInflater,container: ViewGroup?,savedInstanceState: Bundle?): View {
        _binding = FragmentCompanyListBinding.inflate(inflater, container, false)
        setupRecyclerView()
        return binding.root
    }

    private fun setupRecyclerView() {
        val companyListAdapter = CompanyListAdapter(
            onDeleteClicked = { company ->
                deleteCompany(company)
            },
            onNotifyClicked = { company ->
                notifyCompany(company)
            }
        )

        binding.selectedCompaniesRecyclerView.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = companyListAdapter
        }

        // Load the selected companies into the adapter
        companyListAdapter.submitList(CompanyListRepository.getSelectedCompanies())
    }

    private fun deleteCompany(company: Match) {
        AlertDialog.Builder(requireContext())
            .setTitle("Confirm Deletion")
            .setMessage("Are you sure you want to remove ${company.name} from your list?")
            .setPositiveButton("Yes") { _, _ ->
                CompanyListRepository.removeCompany(company)
                binding.selectedCompaniesRecyclerView.adapter?.notifyDataSetChanged()
                Toast.makeText(context, "${company.name} removed successfully.", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("No", null)
            .create()
            .show()
    }

    private fun notifyCompany(company: Match) {
        // Use actual problem details and other data
        val problemDetails = arguments?.getString("problemDetails") ?: "Default problem description"
        val category = arguments?.getString("selectedCategory") ?: "Default category"
        val selectedTags = arguments?.getStringArray("selectedTags") ?: arrayOf("DefaultTag")

        // Log for debugging purposes
        println("Notify: ProblemDetails=$problemDetails, Category=$category, Tags=${selectedTags.joinToString()}")

        // Navigate to InboxFragment
        val companyIds = intArrayOf(company.ranking)

        val action = CompanyListFragmentDirections.actionCompanyListFragmentToInboxFragment(
            problemDetails = problemDetails,
            category = category,
            selectedTags = selectedTags,
            companyIds = companyIds
        )
        findNavController().navigate(action)

        Toast.makeText(requireContext(), "Notify clicked for ${company.name}", Toast.LENGTH_SHORT).show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
