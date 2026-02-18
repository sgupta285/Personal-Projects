//Description: This file provides utility functions for encrypting and decrypting sensitive data, such as passwords or tokens.
//
//Functions:
//generateKey(): Generates a 256-bit AES encryption key.
//encrypt(data: String, secretKey: SecretKey): Encrypts a given string using the provided secret key and returns the encrypted string (Base64 format).
//decrypt(data: String, secretKey: SecretKey): Decrypts an encrypted string using the provided secret key and returns the original string.
//getKeyFromBytes(keyBytes: ByteArray): Converts a byte array into a SecretKey object.

//How to Use: The team working on user authentication and secure data handling can use this utility for encrypting passwords and securely storing sensitive information.



package com.cs407.connectech.utils

import android.util.Base64
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.SecretKeySpec

object EncryptionUtil {
    private const val ALGORITHM = "AES"

    fun generateKey(): SecretKey {
        val keyGen = KeyGenerator.getInstance(ALGORITHM)
        keyGen.init(256) // AES-256
        return keyGen.generateKey()
    }

    fun encrypt(data: String, secretKey: SecretKey): String {
        val cipher = Cipher.getInstance(ALGORITHM)
        cipher.init(Cipher.ENCRYPT_MODE, secretKey)
        val encryptedBytes = cipher.doFinal(data.toByteArray())
        return Base64.encodeToString(encryptedBytes, Base64.DEFAULT)
    }

    fun decrypt(data: String, secretKey: SecretKey): String {
        val cipher = Cipher.getInstance(ALGORITHM)
        cipher.init(Cipher.DECRYPT_MODE, secretKey)
        val decodedBytes = Base64.decode(data, Base64.DEFAULT)
        return String(cipher.doFinal(decodedBytes))
    }

    fun getKeyFromBytes(keyBytes: ByteArray): SecretKey {
        return SecretKeySpec(keyBytes, ALGORITHM)
    }
}
