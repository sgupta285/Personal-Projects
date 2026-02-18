package com.cs407.connectech.ui.main

import android.os.Bundle
import android.util.Log
import android.view.*
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.fragment.findNavController
import androidx.room.Room
import com.cs407.connectech.R
import com.cs407.connectech.data.AppDatabase
import com.cs407.connectech.databinding.FragmentProblemSubmissionBinding
import com.cs407.connectech.repository.FakeAuthRepository
import com.cs407.connectech.repository.FakeMatchRepository
import com.cs407.connectech.viewmodel.AuthViewModel
import com.cs407.connectech.viewmodel.AuthViewModelFactory
import com.cs407.connectech.viewmodel.MatchViewModel
import com.cs407.connectech.viewmodel.MatchViewModelFactory
import com.google.android.material.chip.Chip

class ProblemSubmissionFragment : Fragment() {

    private var _binding: FragmentProblemSubmissionBinding? = null
    private val binding get() = _binding!!
    private lateinit var authViewModel: AuthViewModel
    private lateinit var matchViewModel: MatchViewModel

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentProblemSubmissionBinding.inflate(inflater, container, false)

        setupViewModels()
        setupUI()
        return binding.root
    }

    private fun setupViewModels() {
        val db = Room.databaseBuilder(requireContext(), AppDatabase::class.java, "app_db").build()
        val authRepo = FakeAuthRepository(db.userDao())
        authViewModel = ViewModelProvider(this, AuthViewModelFactory(authRepo))[AuthViewModel::class.java]
        matchViewModel = ViewModelProvider(this, MatchViewModelFactory(FakeMatchRepository(requireContext())))[MatchViewModel::class.java]
    }

    private fun setupUI() {
        val categories = listOf("Large Business", "Medium Business", "Small Business", "Startup")
        val categoryAdapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_item, categories)
        categoryAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        binding.categoryDropdown.adapter = categoryAdapter

        val repository = FakeMatchRepository(requireContext())
        val tags = repository.getAllCompanies().map { it.industry }.distinct()

        tags.forEach { tag ->
            val chip = Chip(requireContext())
            chip.text = tag
            chip.isCheckable = true
            binding.tagChipGroup.addView(chip)
        }

        binding.submitButton.setOnClickListener {
            val problemDetails = binding.projectDetailsInput.text?.toString()?.trim() ?: ""
            val selectedCategory = binding.categoryDropdown.selectedItem?.toString()?.trim() ?: ""
            val selectedChipId = binding.tagChipGroup.checkedChipId
            val selectedTag = if (selectedChipId != View.NO_ID) {
                binding.tagChipGroup.findViewById<Chip>(selectedChipId)?.text?.toString()?.trim() ?: ""
            } else ""

            if (problemDetails.isEmpty()) {
                binding.projectDetailsInput.error = "Enter the project details."
            } else if (selectedCategory.isEmpty()) {
                Toast.makeText(requireContext(), "Select a category.", Toast.LENGTH_SHORT).show()
            } else if (selectedTag.isEmpty()) {
                Toast.makeText(requireContext(), "Select a tag.", Toast.LENGTH_SHORT).show()
            } else {
                submitProblem(problemDetails, selectedCategory, selectedTag)
            }
        }
    }

    private fun submitProblem(problemDetails: String, category: String, selectedTag: String) {
        binding.progressBar.visibility = View.VISIBLE
        binding.submitButton.isEnabled = false

        authViewModel.submitProblem(problemDetails, category)
            .observe(viewLifecycleOwner) { result ->
                binding.progressBar.visibility = View.GONE
                binding.submitButton.isEnabled = true

                result.onSuccess { success ->
                    if (success) {
                        // Navigate to BestMatchesFragment
                        val action = ProblemSubmissionFragmentDirections.actionProblemSubmissionFragmentToBestMatchesFragment(
                            selectedTag = selectedTag,
                            selectedCategory = category
                        )
                        findNavController().navigate(action)

                        Toast.makeText(
                            requireContext(),
                            "Problem submitted successfully!",
                            Toast.LENGTH_SHORT
                        ).show()
                    } else {
                        Toast.makeText(
                            requireContext(),
                            "Submission failed: Unknown error.",
                            Toast.LENGTH_SHORT
                        ).show()
                        Log.e("ProblemSubmission", "Submission failed: Unknown error.")
                    }
                }.onFailure { exception ->
                    Toast.makeText(
                        requireContext(),
                        "Submission failed: ${exception.message}",
                        Toast.LENGTH_SHORT
                    ).show()
                    Log.e("ProblemSubmission", "Submission failed: ${exception.message}")
                }
            }
    }


    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
