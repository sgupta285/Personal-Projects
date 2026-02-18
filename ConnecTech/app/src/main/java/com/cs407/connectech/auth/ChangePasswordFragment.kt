package com.cs407.connectech.auth

import android.os.Bundle
import android.view.*
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import com.cs407.connectech.MyApplication
import com.cs407.connectech.R
import com.cs407.connectech.databinding.FragmentChangePasswordBinding
import com.cs407.connectech.repository.FakeAuthRepository
import com.cs407.connectech.viewmodel.AuthViewModel
import com.cs407.connectech.viewmodel.AuthViewModelFactory

class ChangePasswordFragment : Fragment() {
    private var _binding: FragmentChangePasswordBinding? = null
    private val binding get() = _binding!!

    private val args: ChangePasswordFragmentArgs by navArgs()
    private lateinit var authViewModel: AuthViewModel

    override fun onCreateView(
        inflater: LayoutInflater,container: ViewGroup?,savedInstanceState: Bundle?
    ): View {
        _binding = FragmentChangePasswordBinding.inflate(inflater, container, false)

        val appDatabase = (requireContext().applicationContext as MyApplication).database
        val authRepo = FakeAuthRepository(appDatabase.userDao())
        val factory = AuthViewModelFactory(authRepo)
        authViewModel = ViewModelProvider(this, factory).get(AuthViewModel::class.java)

        setupListeners()
        observeViewModel()

        return binding.root
    }

    private fun setupListeners() {
        binding.changePasswordButton.setOnClickListener {
            val newPassword = binding.newPasswordEditText.text.toString().trim()
            val confirmPassword = binding.confirmNewPasswordEditText.text.toString().trim()

            if (newPassword.isNotEmpty() && confirmPassword.isNotEmpty()) {
                if (newPassword == confirmPassword) {
                    // Call ViewModel to change password
                    authViewModel.changePassword(args.email, newPassword)
                } else {
                    Toast.makeText(requireContext(), "Passwords do not match!", Toast.LENGTH_SHORT).show()
                }
            } else {
                Toast.makeText(requireContext(), "Please fill all fields", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun observeViewModel() {
        authViewModel.changePasswordResult.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                Toast.makeText(requireContext(), "Password changed successfully!", Toast.LENGTH_SHORT).show()
                findNavController().navigate(R.id.action_changePasswordFragment_to_loginFragment)
            }.onFailure {
                Toast.makeText(requireContext(), "Failed to change password: ${it.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
