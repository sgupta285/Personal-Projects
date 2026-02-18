// File: SettingsFragment.kt
package com.cs407.connectech.ui.main

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.fragment.findNavController
import androidx.room.Room
import com.cs407.connectech.R
import com.cs407.connectech.data.AppDatabase
import com.cs407.connectech.databinding.FragmentSettingsBinding
import com.cs407.connectech.repository.FakeAuthRepository
import com.cs407.connectech.viewmodel.AuthViewModel
import com.cs407.connectech.viewmodel.AuthViewModelFactory

class SettingsFragment : Fragment() {

    private var _binding: FragmentSettingsBinding? = null
    private val binding get() = _binding!!

    // Initialize AuthViewModel
    private lateinit var authViewModel: AuthViewModel
    private lateinit var authViewModelFactory: AuthViewModelFactory

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentSettingsBinding.inflate(inflater, container, false)

        // Build the DB and get UserDao
        val db = Room.databaseBuilder(requireContext(), AppDatabase::class.java, "app_db").build()
        val fakeAuthRepository = FakeAuthRepository(db.userDao())

        // Initialize AuthViewModel with Factory
        authViewModelFactory = AuthViewModelFactory(fakeAuthRepository)
        authViewModel = ViewModelProvider(this, authViewModelFactory)[AuthViewModel::class.java]

        setupUI()
        observeLogoutResult()

        return binding.root
    }

    private fun setupUI() {

        // Observe the current user's email
        authViewModel.currentUserEmail.observe(viewLifecycleOwner) { email ->
            binding.etEmail.setText(email)
        }

        // Fetch the email when the UI is set up
        authViewModel.fetchCurrentUserEmail()

        //binding.etEmail.setText("john.doe@example.com")

        binding.btnOngoingContract.setOnClickListener {
            Toast.makeText(requireContext(), "Ongoing Contract Clicked", Toast.LENGTH_SHORT).show()
        }

        binding.btnPreviousContract.setOnClickListener {
            Toast.makeText(requireContext(), "Previous Contract Clicked", Toast.LENGTH_SHORT).show()
        }

        binding.btnScannedDocuments.setOnClickListener {
            Toast.makeText(requireContext(), "Scanned Documents Clicked", Toast.LENGTH_SHORT).show()
        }

        binding.btnProgress.setOnClickListener {
            Toast.makeText(requireContext(), "Progress Clicked", Toast.LENGTH_SHORT).show()
        }

        binding.btnaboutus.setOnClickListener {
            Toast.makeText(requireContext(), "About us Clicked", Toast.LENGTH_SHORT).show()
        }

        binding.btnLogout.setOnClickListener {
            handleLogout()
        }
    }

    private fun handleLogout() {
        authViewModel.logout()
        Toast.makeText(requireContext(), "Logged out successfully", Toast.LENGTH_SHORT).show()
        findNavController().navigate(R.id.action_settingsFragment_to_loginFragment)
    }

    private fun observeLogoutResult() {
        // If logout had async logic, observe here.
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
