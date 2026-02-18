package com.cs407.connectech.auth

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.fragment.findNavController
import com.cs407.connectech.MyApplication
import com.cs407.connectech.R
import com.cs407.connectech.databinding.FragmentForgotPasswordBinding
import com.cs407.connectech.repository.FakeAuthRepository
import com.cs407.connectech.viewmodel.AuthViewModel
import com.cs407.connectech.viewmodel.AuthViewModelFactory

class ForgotPasswordFragment : Fragment() {
    private var _binding: FragmentForgotPasswordBinding? = null
    private val binding get() = _binding!!

    //Testing something by commenting this
    //private val authViewModel: AuthViewModel by viewModels()

    private lateinit var authViewModel: AuthViewModel

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentForgotPasswordBinding.inflate(inflater, container, false)

        val appDatabase = (requireContext().applicationContext as MyApplication).database
        val authRepo = FakeAuthRepository(appDatabase.userDao())
        val factory = AuthViewModelFactory(authRepo)
        authViewModel = ViewModelProvider(this, factory).get(AuthViewModel::class.java)

        setupListeners()
        observeViewModel()
        return binding.root
    }

    private fun setupListeners() {
        binding.resetPasswordButton.setOnClickListener {
            val email = binding.emailEditText.text.toString().trim()
            if (email.isNotEmpty()) {
                Toast.makeText(context, "Reset Password Button Clicked", Toast.LENGTH_SHORT).show()
                authViewModel.resetPassword(email)
            } else {
                Toast.makeText(context, "Please enter your email", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun observeViewModel() {
        authViewModel.resetPasswordResult.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                showAlertDialog()
            }.onFailure {
                Toast.makeText(context, it.message ?: "Reset failed", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun showAlertDialog() {
        AlertDialog.Builder(requireContext())
            .setTitle("Email Verified!")
            .setMessage("You can reset your password now.")
            .setPositiveButton("OK") { _, _ ->
                val email = binding.emailEditText.text.toString().trim()
                // Navigate to ChangePasswordFragment with the email argument
                val action = ForgotPasswordFragmentDirections.actionForgotPasswordFragmentToChangePasswordFragment(email)
                findNavController().navigate(action)
            }
            .setCancelable(false)
            .show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}