class ValidationUtils {
  // Email validation
  static bool isValidEmail(String email) {
    final emailRegExp = RegExp(
      r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    );
    return emailRegExp.hasMatch(email);
  }

  // Phone number validation (numeric only)
  static bool isValidPhoneNumber(String phoneNumber) {
    final phoneRegExp = RegExp(r'^\d+$');
    return phoneRegExp.hasMatch(phoneNumber);
  }

  // Age validation
  static bool isValidAge(String age) {
    try {
      final ageInt = int.parse(age);
      return ageInt > 0 && ageInt <= 150;
    } catch (e) {
      return false;
    }
  }

  // Name validation
  static bool isValidName(String name) {
    return name.trim().isNotEmpty;
  }

  // Get email error message
  static String? validateEmail(String? email) {
    if (email == null || email.isEmpty) {
      return 'Email is required';
    }
    if (!isValidEmail(email)) {
      return 'Please enter a valid email address';
    }
    return null;
  }

  // Get name error message
  static String? validateName(String? name) {
    if (name == null || name.isEmpty) {
      return 'Name is required';
    }
    if (name.trim().length < 2) {
      return 'Name must be at least 2 characters long';
    }
    return null;
  }

  // Get phone number error message
  static String? validatePhoneNumber(String? phoneNumber) {
    if (phoneNumber != null && phoneNumber.isNotEmpty) {
      if (!isValidPhoneNumber(phoneNumber)) {
        return 'Phone number must contain only digits';
      }
      if (phoneNumber.length < 10) {
        return 'Phone number must be at least 10 digits';
      }
    }
    return null;
  }

  // Get age error message
  static String? validateAge(String? age) {
    if (age != null && age.isNotEmpty) {
      if (!isValidAge(age)) {
        return 'Please enter a valid age (1-150)';
      }
    }
    return null;
  }
}
