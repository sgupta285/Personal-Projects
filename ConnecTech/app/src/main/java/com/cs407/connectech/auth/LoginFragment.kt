package com.cs407.connectech.auth

import android.os.Bundle
import android.view.*
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.fragment.findNavController
import com.cs407.connectech.MyApplication
import com.cs407.connectech.R
import com.cs407.connectech.databinding.FragmentLoginBinding
import com.cs407.connectech.repository.FakeAuthRepository
import com.cs407.connectech.viewmodel.AuthViewModel
import com.cs407.connectech.viewmodel.AuthViewModelFactory

class LoginFragment : Fragment() {
    private var _binding: FragmentLoginBinding? = null
    private val binding get() = _binding!!

    private lateinit var authViewModel: AuthViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentLoginBinding.inflate(inflater, container, false)

        // Get the shared database instance from MyApplication
        val appDatabase = (requireContext().applicationContext as MyApplication).database
        val authRepo = FakeAuthRepository(appDatabase.userDao())
        val factory = AuthViewModelFactory(authRepo)
        authViewModel = ViewModelProvider(this, factory).get(AuthViewModel::class.java)

        setupListeners()
        observeLoginResult()

        return binding.root
    }

    private fun setupListeners() {
        // Login Button Logic
        binding.loginButton.setOnClickListener {
            val email = binding.emailEditText.text.toString().trim()
            val password = binding.passwordEditText.text.toString().trim()
            if (email.isNotEmpty() && password.isNotEmpty()) {
                authViewModel.login(email, password)
            } else {
                Toast.makeText(requireContext(), "Please enter email and password", Toast.LENGTH_SHORT).show()
            }
        }

        // Back Button Logic
        binding.backButton.setOnClickListener {
            findNavController().navigateUp() // Navigate back to the previous page in the navigation stack
        }

        // Forgot Password Logic
        binding.forgotPasswordTextView.setOnClickListener {
            findNavController().navigate(R.id.action_loginFragment_to_forgotPasswordFragment)
        }
    }

    private fun observeLoginResult() {
        authViewModel.loginResult.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                Toast.makeText(requireContext(), "Login successful!", Toast.LENGTH_SHORT).show()
                findNavController().navigate(R.id.action_loginFragment_to_problemSubmissionFragment)
            }.onFailure {
                Toast.makeText(requireContext(), "Login failed: ${it.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
