package com.cs407.connectech.ui.main

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.cs407.connectech.R
import com.cs407.connectech.databinding.FragmentLandingPageBinding

class LandingPage : Fragment() {

    private var _binding: FragmentLandingPageBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        _binding = FragmentLandingPageBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Set click listener for Login Button
        binding.loginButton.setOnClickListener {
            findNavController().navigate(R.id.action_landingPage_to_loginFragment)
        }

        // Set click listener for Create Account Button
        binding.createAccountButton.setOnClickListener {
            findNavController().navigate(R.id.action_landingPage_to_registerFragment)
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
