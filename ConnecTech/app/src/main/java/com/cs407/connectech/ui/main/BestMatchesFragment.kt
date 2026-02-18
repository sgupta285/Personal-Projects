package com.cs407.connectech.ui.main

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import androidx.recyclerview.widget.LinearLayoutManager
import com.cs407.connectech.databinding.FragmentBestMatchesBinding
import com.cs407.connectech.model.Match
import com.cs407.connectech.repository.FakeMatchRepository
import com.cs407.connectech.ui.main.adapter.MatchAdapter
import com.cs407.connectech.viewmodel.MatchViewModel
import com.cs407.connectech.viewmodel.MatchViewModelFactory

class BestMatchesFragment : Fragment() {

    private var _binding: FragmentBestMatchesBinding? = null
    private val binding get() = _binding!!
    private lateinit var matchViewModel: MatchViewModel
    private lateinit var matchAdapter: MatchAdapter
    private val selectedCompanies = mutableListOf<Match>()
    private val args: BestMatchesFragmentArgs by navArgs()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentBestMatchesBinding.inflate(inflater, container, false)

        // Initialize ViewModel
        matchViewModel = ViewModelProvider(
            this,
            MatchViewModelFactory(FakeMatchRepository(requireContext()))
        )[MatchViewModel::class.java]

        // Set up RecyclerView
        setupRecyclerView()

        // Observe LiveData for updates
        observeData()

        // Fetch best matches based on arguments
        val args = BestMatchesFragmentArgs.fromBundle(requireArguments())
        matchViewModel.fetchBestMatches(args.selectedTag, args.selectedCategory)

        return binding.root
    }

    private fun setupRecyclerView() {
        matchAdapter = MatchAdapter { selectedMatch ->
            val action = BestMatchesFragmentDirections
                .actionBestMatchesFragmentToCompanySelectedFragment(companyId = selectedMatch.ranking)
            findNavController().navigate(action)
        }

        binding.bestMatchesRecyclerView.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = matchAdapter
        }
    }

    private fun observeData() {
        matchViewModel.bestMatches.observe(viewLifecycleOwner) { matches ->
            if (matches.isNotEmpty()) {
                matchAdapter.submitList(matches)
                updateUI(matches)
            } else {
                // Handle case where no matches are found
                Toast.makeText(context, "No matches found for the selected category.", Toast.LENGTH_SHORT).show()
                // Consider navigating back or showing a placeholder UI
            }
        }

        matchViewModel.error.observe(viewLifecycleOwner) { errorMessage ->
            Toast.makeText(context, "Error: $errorMessage", Toast.LENGTH_SHORT).show()
        }
    }

    private fun updateUI(matches: List<Match>) {
        binding.bestMatchesTitle.text = "Top ${args.selectedTag} Companies"
        binding.bestMatchesSubtitle.text = "Here are ${matches.size} companies that excel in ${args.selectedTag}"
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}