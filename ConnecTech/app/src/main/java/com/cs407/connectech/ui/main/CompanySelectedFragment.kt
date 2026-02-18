package com.cs407.connectech.ui.main

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import com.cs407.connectech.databinding.FragmentCompanySelectedBinding
import com.cs407.connectech.model.Match
import com.cs407.connectech.repository.CompanyListRepository
import com.cs407.connectech.repository.FakeMatchRepository

class CompanySelectedFragment : Fragment() {

    private var _binding: FragmentCompanySelectedBinding? = null
    private val binding get() = _binding!!
    private val args: CompanySelectedFragmentArgs by navArgs()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentCompanySelectedBinding.inflate(inflater, container, false)

        // Fetch company details
        val match = fetchCompanyDetails(args.companyId)

        // Populate UI
        match?.let {
            binding.companyName.text = it.name
            binding.companyDetails.text = """
                Ranking: ${it.ranking}
                Name: ${it.name}
                Market Cap: ${it.marketCap}
                Stock Symbol: ${it.stockSymbol}
                Country: ${it.country}
                Sector: ${it.sector}
                Industry: ${it.industry}
            """.trimIndent()
        }

        // Handle "Select Partner" button
        binding.selectPartnerButton.setOnClickListener {
            match?.let {
                CompanyListRepository.addCompany(it)
                showConfirmationDialog()
            }
        }

        return binding.root
    }

    private fun fetchCompanyDetails(companyId: Int): Match? {
        val repository = FakeMatchRepository(requireContext())
        return repository.getCompanyById(companyId)
    }

    private fun showConfirmationDialog() {
        AlertDialog.Builder(requireContext())
            .setTitle("Partner Selected!")
            .setMessage("This partner has been added to your list.")
            .setPositiveButton("OK") { dialog, _ ->
                dialog.dismiss()
                findNavController().navigateUp() // Navigate back to CompanyListFragment
            }
            .create()
            .show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
