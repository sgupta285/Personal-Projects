// File: RegisterFragment.kt
package com.cs407.connectech.auth

import android.app.AlertDialog
import android.os.Bundle
import android.view.*
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.fragment.findNavController
import com.cs407.connectech.MyApplication
import com.cs407.connectech.R
import com.cs407.connectech.databinding.FragmentRegisterBinding
import com.cs407.connectech.repository.FakeAuthRepository
import com.cs407.connectech.viewmodel.AuthViewModel
import com.cs407.connectech.viewmodel.AuthViewModelFactory

class RegisterFragment : Fragment() {
    private var _binding: FragmentRegisterBinding? = null
    private val binding get() = _binding!!

    private lateinit var authViewModel: AuthViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentRegisterBinding.inflate(inflater, container, false)

        // Get the shared database from the Application class
        val appDatabase = (requireContext().applicationContext as MyApplication).database
        val authRepo = FakeAuthRepository(appDatabase.userDao())
        val factory = AuthViewModelFactory(authRepo)
        authViewModel = ViewModelProvider(this, factory).get(AuthViewModel::class.java)

        return binding.root
    }

    // Move listener setup to onViewCreated so the view is fully initialized
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupListeners()
        observeRegisterResult()
    }

    private fun setupListeners() {
        binding.magicButton.setOnClickListener {
            val email = binding.emailEditText.text.toString().trim()
            val password = binding.passwordEditText.text.toString().trim()
            if (email.isNotEmpty() && password.isNotEmpty()) {
                authViewModel.register(email, password)
            } else {
                Toast.makeText(requireContext(), "Please enter email and password", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun observeRegisterResult() {
        authViewModel.registerResult.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                Toast.makeText(requireContext(), "Registration successful!", Toast.LENGTH_SHORT).show()
                findNavController().navigate(R.id.action_registerFragment_to_loginFragment)
            }.onFailure {
                Toast.makeText(requireContext(), "Registration failed: ${it.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun showLoading(isLoading: Boolean) {
        binding.loadingProgressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        binding.magicButton.isEnabled = !isLoading
        // Optionally disable other UI elements while loading
    }


    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
