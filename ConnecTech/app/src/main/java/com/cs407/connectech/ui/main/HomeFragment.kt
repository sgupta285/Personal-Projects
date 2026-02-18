// File: HomeFragment.kt
package com.cs407.connectech.ui.main

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.cs407.connectech.ConnecTechApp
import com.cs407.connectech.databinding.FragmentProblemSubmissionBinding
import com.cs407.connectech.ui.main.adapter.MatchAdapter

class HomeFragment : Fragment() {

    private var _binding: FragmentProblemSubmissionBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View? {
        _binding = FragmentProblemSubmissionBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.submitButton.setOnClickListener {
            // Handle submit action
            Toast.makeText(requireContext(), "Analyze and Match Clicked", Toast.LENGTH_SHORT).show()
            // Navigate to BestMatchesFragment or perform desired action
            //(activity as? ConnecTechApp)?.navigateToFragment(BestMatchesFragment())
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
