# **ConnecTech**

ConnecTech is a sophisticated B2B matchmaking platform aimed at bridging the gap between businesses requiring technology solutions and tech service providers. Designed to offer transparency, efficiency, and trust, ConnecTech provides a seamless environment for businesses to find the right tech partners and for service providers to access a stream of clients aligned with their expertise.

---

## **Table of Contents**

- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)

---

## **Key Features**

### **For Businesses**
- **Effortless Tech Partner Search**: Find pre-vetted service providers tailored to your requirements.
- **Transparent Communication**: Easily negotiate contracts and communicate requirements within the platform.
- **Secure Payments**: Built-in payment integration ensures seamless transactions.
- **Diverse Services**: Support for a range of services including app development, cybersecurity, cloud migration, and more.

### **For Service Providers**
- **Instant Access to Clients**: Access business leads without heavy marketing costs.
- **Optimized Matching**: Work on projects that align with your expertise and capacity.
- **Reputation Building**: Gain ratings and visibility through successfully delivered projects.

---

## **Tech Stack**

### **Frontend**
- **Kotlin**: Robust and modern language for Android app development.
- **XML**: Layout designs ensuring a responsive and dynamic user interface.

### **Backend Integration**
- **Retrofit**: REST API integration with easy-to-use request models (`LoginRequest`, `RegisterRequest`, `ResetPasswordRequest`).

### **Architecture**
- **MVVM (Model-View-ViewModel)**:
  - **Model**: Business logic handled via repositories (e.g., `AuthRepository`, `ProblemRepository`).
  - **ViewModel**: Manages UI-related data and handles LiveData for UI updates.
  - **View**: Fragments for interactive user interfaces (`LoginFragment`, `RegisterFragment`, `ForgotPasswordFragment`).

### **Security**
- **Encryption Utilities**: Ensures secure storage and transfer of sensitive data.
- **Pre-vetted Providers**: Providers undergo rigorous checks before being listed.

### **Dependencies**
- **LiveData**: Reactive data handling for dynamic UI updates.
- **View Binding**: Simplifies XML view references, reducing boilerplate code.

---

## **Architecture Overview**

### **App Initialization**
- `ConnecTechApp` initializes the `AppCompatActivity` and sets the main layout (`fragment_container`).
- Navigation between fragments is managed using `FragmentManager`.

### **Key Components**
1. **Auth Module**:
   - Handles authentication flows such as login, registration, and password reset.
   - `AuthViewModel` interacts with `AuthRepository` to fetch data via API.
2. **Matchmaking Module**:
   - Matches businesses with tech providers based on project details and expertise.
3. **UI Components**:
   - `LoginFragment`, `RegisterFragment`, and `ForgotPasswordFragment` for user interaction.
4. **Utilities**:
   - **`EncryptionUtil`**: Ensures sensitive data is encrypted before storage or transfer.
   - **`Constants`**: Centralized configuration and constant values.

---

## **Project Structure**

### **Directories**
- **`auth`**:
  - Fragments for `Login`, `Register`, and `ForgotPassword`.
  - `AuthViewModel` for managing authentication-related LiveData.
- **`model`**:
  - Data models (`User`, `Provider`, `Match`, `Problem`) representing the app's core entities.
- **`network`**:
  - **`ApiService`**: Defines API endpoints.
  - **`RetrofitClient`**: Configures Retrofit for API communication.
- **`repository`**:
  - **`AuthRepository`**: Handles API calls for authentication.
  - **`ProblemRepository`**: Manages problem submission and retrieval.
  - **`MatchRepository`**: Implements matchmaking logic.
- **`ui.main`**:
  - Contains fragments for profile management, problem submissions, and best matches.
- **`utils`**:
  - **`EncryptionUtil`**: Provides encryption for sensitive data.
  - **`Constants`**: Stores reusable constants.
- **`viewmodel`**:
  - Houses the ViewModels (`AuthViewModel`, `MatchViewModel`) for state management.

### **Resource Files**
- **Layouts**:
  - `fragment_login.xml`, `fragment_register.xml`, `fragment_forgot_password.xml` for respective fragments.
  - Custom designs such as `rounded_edittext.xml` for styled input fields.
- **Drawables**:
  - Icons, background images, and custom shapes.

---

### **Prerequisites**
- **Android Studio**: Version 2022.3 or higher.
- **Java**: OpenJDK 17 or higher.
- **Gradle**: Version 8.7 or higher.
- **Minimum SDK**: 24 (Android 7.0 Nougat).
- **Target SDK**: 35 (Android 14).

### **Setup**
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ConnecTech.git
