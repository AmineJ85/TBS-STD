// Function to show notification
function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `system-notification ${type}`;
  notification.textContent = message;
  
  // Add close button
  const closeBtn = document.createElement('button');
  closeBtn.innerHTML = '&times;';
  closeBtn.style.background = 'none';
  closeBtn.style.border = 'none';
  closeBtn.style.fontSize = '1.2rem';
  closeBtn.style.cursor = 'pointer';
  closeBtn.style.marginLeft = 'auto';
  closeBtn.addEventListener('click', () => {
    document.body.removeChild(notification);
  });
  
  notification.appendChild(closeBtn);
  
  // Add to body
  document.body.appendChild(notification);
  
  // Auto-remove after 8 seconds
  setTimeout(() => {
    if (document.body.contains(notification)) {
      document.body.removeChild(notification);
    }
  }, 8000);
}

document.addEventListener('DOMContentLoaded', function() {
  // Check for system messages
  const systemMessageElement = document.getElementById('system-message');
  if (systemMessageElement) {
    const message = systemMessageElement.dataset.message;
    if (message) {
      // Determine message type
      let messageType = 'info';
      if (message.toLowerCase().includes('confirmed') || message.toLowerCase().includes('success')) {
        messageType = 'success';
      } else if (message.toLowerCase().includes('invalid') || message.toLowerCase().includes('error') || message.toLowerCase().includes('expired')) {
        messageType = 'error';
      }
      
      // Show notification
      showNotification(message, messageType);
    }
  }
  
  // Create UI elements dynamically
  function createUIElements() {
    // Create top bar
    const topBar = document.createElement('div');
    topBar.className = 'top-bar';
    
    // Create links container
    const linksContainer = document.createElement('div');
    linksContainer.className = 'links-container';
    
    // Create website links
    const websiteLinks = [
      { text: 'Website', href: 'https://tunis-business-school.tn/' },
      { text: 'Handbook', href: 'https://tunis-business-school.tn/academics/bachelor-business-administration/' },
      { text: 'Archive', href: 'https://tbsarchive.wixsite.com/tbsarchive/bdm' }
    ];
    
    websiteLinks.forEach(link => {
      const a = document.createElement('a');
      a.href = link.href;
      a.textContent = link.text;
      a.className = 'site-link';
      a.target = '_blank'; // Open in new tab
      linksContainer.appendChild(a);
    });
    
    topBar.appendChild(linksContainer);
    
    // Create main content container
    const mainContent = document.createElement('div');
    mainContent.className = 'main-content';
    
    // Create wrapper to control vertical positioning
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'content-wrapper';
    
    // Create welcome image
    const welcomeImg = document.createElement('img');
    welcomeImg.src = 'static/images/TBS_welcome.png';
    welcomeImg.alt = 'TBS Welcome';
    welcomeImg.className = 'welcome-image';
    
    // Create auth buttons container - stacked vertically
    const authButtons = document.createElement('div');
    authButtons.className = 'auth-buttons';
    
    const loginBtn = document.createElement('button');
    loginBtn.className = 'neumorphic auth-btn';
    loginBtn.id = 'login-btn';
    loginBtn.textContent = 'Login';
    
    const registerBtn = document.createElement('button');
    registerBtn.className = 'neumorphic auth-btn';
    registerBtn.id = 'register-btn';
    registerBtn.textContent = 'Register';
    
    authButtons.appendChild(loginBtn);
    authButtons.appendChild(registerBtn);
    
    // Add elements to content wrapper
    contentWrapper.appendChild(welcomeImg);
    contentWrapper.appendChild(authButtons);
    
    // Add content wrapper to main content
    mainContent.appendChild(contentWrapper);
    
    // Create modal overlay
    const modalOverlay = document.createElement('div');
    modalOverlay.id = 'modal-overlay';
    modalOverlay.className = 'modal-overlay hidden';
    
    // Create registration modal
    const registrationModal = document.createElement('div');
    registrationModal.id = 'registration-modal';
    registrationModal.className = 'modal hidden';
    
    const registrationContent = document.createElement('div');
    registrationContent.className = 'modal-content neumorphic';
    
    const closeRegBtn = document.createElement('button');
    closeRegBtn.className = 'modal-close-btn wiggle neumorphic';
    closeRegBtn.id = 'modal-close-btn';
    closeRegBtn.setAttribute('aria-label', 'Close registration form');
    closeRegBtn.innerHTML = '&times;';
    
    const regTitle = document.createElement('h2');
    regTitle.textContent = 'Student Registration';
    
    const regForm = document.createElement('form');
    regForm.id = 'registration-form';
    
    // Create registration form fields
    const formFields = [
      { name: 'firstName', icon: 'fa-user-o', placeholder: 'First Name', type: 'text' },
      { name: 'lastName', icon: 'fa-user-o', placeholder: 'Last Name', type: 'text' },
      { name: 'nic', icon: 'fa-id-card', placeholder: 'National Identity Card Number', type: 'text' },
      { name: 'email', icon: 'fa-envelope', placeholder: 'someone@tbs.u-tunis.tn', type: 'email' }
    ];
    
    formFields.forEach(field => {
      const inputGroup = document.createElement('div');
      inputGroup.className = 'input-group';
      
      const iconSpan = document.createElement('span');
      iconSpan.className = 'input-icon';
      const icon = document.createElement('i');
      icon.className = `fa ${field.icon}`;
      iconSpan.appendChild(icon);
      
      const input = document.createElement('input');
      input.type = field.type;
      input.name = field.name;
      input.placeholder = field.placeholder;
      input.required = true;
      
      const fieldMsg = document.createElement('div');
      fieldMsg.className = 'field-message';
      
      inputGroup.appendChild(iconSpan);
      inputGroup.appendChild(input);
      inputGroup.appendChild(fieldMsg);
      
      regForm.appendChild(inputGroup);
    });
    
    // Create password field
    const passwordGroup = document.createElement('div');
    passwordGroup.className = 'input-group password-group';
    
    const passwordIcon = document.createElement('span');
    passwordIcon.className = 'input-icon';
    const pwdIcon = document.createElement('i');
    pwdIcon.className = 'fa fa-key';
    passwordIcon.appendChild(pwdIcon);
    
    const passwordInput = document.createElement('input');
    passwordInput.type = 'password';
    passwordInput.id = 'password';
    passwordInput.name = 'password';
    passwordInput.placeholder = 'Enter Password';
    passwordInput.required = true;
    passwordInput.minLength = 8;
    
    const togglePassword = document.createElement('span');
    togglePassword.className = 'toggle-password';
    togglePassword.dataset.target = 'password';
    const eyeIcon = document.createElement('i');
    eyeIcon.className = 'fa fa-eye';
    togglePassword.appendChild(eyeIcon);
    
    const passwordReqs = document.createElement('div');
    passwordReqs.className = 'password-requirements';
    
    const reqsTitle = document.createElement('p');
    reqsTitle.textContent = 'Password must contain:';
    
    const reqsList = document.createElement('ul');
    
    const requirements = [
      { req: 'length', text: 'At least 8 characters' },
      { req: 'uppercase', text: 'At least 1 uppercase letter' },
      { req: 'lowercase', text: 'At least 1 lowercase letter' },
      { req: 'number', text: 'At least 1 number' },
      { req: 'special', text: 'At least 1 special character' }
    ];
    
    requirements.forEach(req => {
      const li = document.createElement('li');
      li.className = 'requirement';
      li.dataset.requirement = req.req;
      li.textContent = req.text;
      reqsList.appendChild(li);
    });
    
    passwordReqs.appendChild(reqsTitle);
    passwordReqs.appendChild(reqsList);
    
    const passwordMsg = document.createElement('div');
    passwordMsg.className = 'field-message';
    
    passwordGroup.appendChild(passwordIcon);
    passwordGroup.appendChild(passwordInput);
    passwordGroup.appendChild(togglePassword);
    passwordGroup.appendChild(passwordReqs);
    passwordGroup.appendChild(passwordMsg);
    
    regForm.appendChild(passwordGroup);
    
    // Create confirm password field
    const confirmGroup = document.createElement('div');
    confirmGroup.className = 'input-group password-group confirm-password-group';
    
    const confirmIcon = document.createElement('span');
    confirmIcon.className = 'input-icon';
    const confIcon = document.createElement('i');
    confIcon.className = 'fa fa-key';
    confirmIcon.appendChild(confIcon);
    
    const confirmInput = document.createElement('input');
    confirmInput.type = 'password';
    confirmInput.id = 'confirm-password';
    confirmInput.name = 'confirmPassword';
    confirmInput.placeholder = 'Repeat Password';
    confirmInput.required = true;
    confirmInput.minLength = 8;
    
    const toggleConfirm = document.createElement('span');
    toggleConfirm.className = 'toggle-password';
    toggleConfirm.dataset.target = 'confirm-password';
    const confEyeIcon = document.createElement('i');
    confEyeIcon.className = 'fa fa-eye';
    toggleConfirm.appendChild(confEyeIcon);
    
    const confirmMsg = document.createElement('div');
    confirmMsg.className = 'field-message';
    
    confirmGroup.appendChild(confirmIcon);
    confirmGroup.appendChild(confirmInput);
    confirmGroup.appendChild(toggleConfirm);
    confirmGroup.appendChild(confirmMsg);
    
    regForm.appendChild(confirmGroup);
    
    // Create success message and submit button
    const successMsg = document.createElement('div');
    successMsg.id = 'success-message';
    successMsg.className = 'success-message';
    
    const submitBtn = document.createElement('button');
    submitBtn.type = 'submit';
    submitBtn.className = 'neumorphic form-submit-btn';
    submitBtn.textContent = 'Register';
    
    regForm.appendChild(successMsg);
    regForm.appendChild(submitBtn);
    
    registrationContent.appendChild(closeRegBtn);
    registrationContent.appendChild(regTitle);
    registrationContent.appendChild(regForm);
    
    registrationModal.appendChild(registrationContent);
    
    // Create login modal
    const loginModal = document.createElement('div');
    loginModal.id = 'login-modal';
    loginModal.className = 'modal hidden';
    
    const loginContent = document.createElement('div');
    loginContent.className = 'modal-content neumorphic';
    
    const closeLoginBtn = document.createElement('button');
    closeLoginBtn.className = 'modal-close-btn wiggle neumorphic';
    closeLoginBtn.id = 'login-close-btn';
    closeLoginBtn.innerHTML = '&times;';
    
    const loginTitle = document.createElement('h2');
    loginTitle.id = 'login-modal-title';
    loginTitle.textContent = 'Login';
    
    const loginForm = document.createElement('form');
    loginForm.id = 'login-form';
    loginForm.noValidate = true; // Disable browser's default validation
    
    // Create login form fields
    const loginEmailGroup = document.createElement('div');
    loginEmailGroup.className = 'input-group';
    
    const loginEmailIcon = document.createElement('span');
    loginEmailIcon.className = 'input-icon';
    const loginEmIcon = document.createElement('i');
    loginEmIcon.className = 'fa fa-envelope';
    loginEmailIcon.appendChild(loginEmIcon);
    
    const loginEmailInput = document.createElement('input');
    loginEmailInput.type = 'text'; // Use text type to avoid browser validation
    loginEmailInput.name = 'email';
    loginEmailInput.placeholder = 'Email';
    loginEmailInput.required = true;
    
    loginEmailGroup.appendChild(loginEmailIcon);
    loginEmailGroup.appendChild(loginEmailInput);
    
    const loginPasswordGroup = document.createElement('div');
    loginPasswordGroup.className = 'input-group password-group';
    
    const loginPasswordIcon = document.createElement('span');
    loginPasswordIcon.className = 'input-icon';
    const loginPwIcon = document.createElement('i');
    loginPwIcon.className = 'fa fa-key';
    loginPasswordIcon.appendChild(loginPwIcon);
    
    const loginPasswordInput = document.createElement('input');
    loginPasswordInput.type = 'password';
    loginPasswordInput.name = 'password';
    loginPasswordInput.placeholder = 'Password';
    loginPasswordInput.required = true;
    loginPasswordInput.minLength = 8;
    
    loginPasswordGroup.appendChild(loginPasswordIcon);
    loginPasswordGroup.appendChild(loginPasswordInput);
    
    const loginError = document.createElement('div');
    loginError.id = 'login-error';
    
    const loginSubmit = document.createElement('button');
    loginSubmit.type = 'submit';
    loginSubmit.className = 'neumorphic form-submit-btn';
    loginSubmit.textContent = 'Login';
    
    loginForm.appendChild(loginEmailGroup);
    loginForm.appendChild(loginPasswordGroup);
    loginForm.appendChild(loginError);
    loginForm.appendChild(loginSubmit);
    
    // Add "Forgot password?" link
    const forgotPasswordLink = document.createElement('a');
    forgotPasswordLink.id = 'forgot-password-link';
    forgotPasswordLink.href = '#';
    forgotPasswordLink.textContent = 'Forgot password?';
    forgotPasswordLink.style.display = 'block';
    forgotPasswordLink.style.marginTop = '8px';
    forgotPasswordLink.style.textAlign = 'center';
    forgotPasswordLink.style.fontSize = '0.85rem';
    forgotPasswordLink.style.color = '#3182ce';
    loginForm.appendChild(forgotPasswordLink);
    
    /* ===== Forgot-password container (hidden by default) ===== */
    const forgotContainer = document.createElement('div');
    forgotContainer.id = 'forgot-container';
    forgotContainer.style.display = 'none';

    // Step 1 — ask for email + national ID
    const fpStep1 = document.createElement('div');
    fpStep1.id = 'fp-step1';
    // Email group
    const fpEmailGroup = document.createElement('div');
    fpEmailGroup.className = 'input-group';
    const fpEmailIcon = document.createElement('span');
    fpEmailIcon.className = 'input-icon';
    fpEmailIcon.innerHTML = '<i class="fa fa-envelope"></i>';
    const fpEmail = document.createElement('input');
    fpEmail.type = 'email';
    fpEmail.placeholder = 'Email';
    fpEmail.required = true;
    fpEmailGroup.appendChild(fpEmailIcon);
    fpEmailGroup.appendChild(fpEmail);

    // National ID group
    const fpNidGroup = document.createElement('div');
    fpNidGroup.className = 'input-group';
    const fpNidIcon = document.createElement('span');
    fpNidIcon.className = 'input-icon';
    fpNidIcon.innerHTML = '<i class="fa fa-id-card"></i>';
    const fpNID = document.createElement('input');
    fpNID.type = 'text';
    fpNID.placeholder = 'National ID';
    fpNID.required = true;
    fpNidGroup.appendChild(fpNidIcon);
    fpNidGroup.appendChild(fpNID);

    fpStep1.appendChild(fpEmailGroup);
    fpStep1.appendChild(fpNidGroup);

    const fpSendBtn = document.createElement('button');
    fpSendBtn.id = 'fp-send-btn';
    fpSendBtn.textContent = 'Send reset code';
    fpSendBtn.className = 'neumorphic form-submit-btn';
    fpStep1.appendChild(fpSendBtn);

    // Step 2 — verify code + set new password
    const fpStep2 = document.createElement('div');
    fpStep2.id = 'fp-step2';
    fpStep2.style.display = 'none';
    // Code group
    const fpCodeGroup = document.createElement('div');
    fpCodeGroup.className = 'input-group';
    const fpCodeIcon = document.createElement('span');
    fpCodeIcon.className = 'input-icon';
    fpCodeIcon.innerHTML = '<i class="fa fa-key"></i>';
    const fpCode = document.createElement('input');
    fpCode.type = 'text';
    fpCode.placeholder = '6-digit code';
    fpCode.required = true;
    fpCode.maxLength = 6;
    fpCodeGroup.appendChild(fpCodeIcon);
    fpCodeGroup.appendChild(fpCode);

    // New password group
    const fpNewPwdGroup = document.createElement('div');
    fpNewPwdGroup.className = 'input-group';
    const fpNewPwdIcon = document.createElement('span');
    fpNewPwdIcon.className = 'input-icon';
    fpNewPwdIcon.innerHTML = '<i class="fa fa-lock"></i>';
    const fpNewPwd = document.createElement('input');
    fpNewPwd.type = 'password';
    fpNewPwd.placeholder = 'New password';
    fpNewPwd.required = true;
    fpNewPwdGroup.appendChild(fpNewPwdIcon);
    fpNewPwdGroup.appendChild(fpNewPwd);

    // Confirm password group
    const fpConfPwdGroup = document.createElement('div');
    fpConfPwdGroup.className = 'input-group';
    const fpConfPwdIcon = document.createElement('span');
    fpConfPwdIcon.className = 'input-icon';
    fpConfPwdIcon.innerHTML = '<i class="fa fa-lock"></i>';
    const fpConfirmPwd = document.createElement('input');
    fpConfirmPwd.type = 'password';
    fpConfirmPwd.placeholder = 'Confirm new password';
    fpConfirmPwd.required = true;
    fpConfPwdGroup.appendChild(fpConfPwdIcon);
    fpConfPwdGroup.appendChild(fpConfirmPwd);

    fpStep2.appendChild(fpCodeGroup);
    fpStep2.appendChild(fpNewPwdGroup);
    fpStep2.appendChild(fpConfPwdGroup);

    // Message paragraph
    const fpMessage = document.createElement('p');
    fpMessage.id = 'fp-message';
    fpMessage.style.marginTop = '10px';

    // Back link
    const backToLoginLink = document.createElement('a');
    backToLoginLink.id = 'back-to-login-link';
    backToLoginLink.href = '#';
    backToLoginLink.textContent = 'Back to login';
    backToLoginLink.style.display = 'block';
    backToLoginLink.style.marginTop = '8px';
    backToLoginLink.style.textAlign = 'center';
    backToLoginLink.style.fontSize = '0.85rem';

    const fpResetBtn = document.createElement('button');
    fpResetBtn.id = 'fp-reset-btn';
    fpResetBtn.textContent = 'Reset password';
    fpResetBtn.className = 'neumorphic form-submit-btn';

    fpStep2.appendChild(fpResetBtn);

    forgotContainer.appendChild(fpStep1);
    forgotContainer.appendChild(fpStep2);
    forgotContainer.appendChild(fpMessage);
    forgotContainer.appendChild(backToLoginLink);

    loginContent.appendChild(closeLoginBtn);
    loginContent.appendChild(loginTitle);
    loginContent.appendChild(loginForm);
    loginContent.appendChild(forgotContainer);
    
    loginModal.appendChild(loginContent);
    
    // Add all elements to the body
    document.body.appendChild(topBar);
    document.body.appendChild(mainContent);
    document.body.appendChild(modalOverlay);
    document.body.appendChild(registrationModal);
    document.body.appendChild(loginModal);
    
    // No sidebar functionality needed anymore
    modalOverlay.addEventListener('click', function() {
      loginModal.classList.add('hidden');
      registrationModal.classList.add('hidden');
      modalOverlay.classList.add('hidden');
    });
  }
  
  // Call the function to create UI elements
  createUIElements();

  // Elements
  const submitBtn = document.querySelector('.form-submit-btn');
  const firstNameInput = document.querySelector('input[name="firstName"]');
  const lastNameInput = document.querySelector('input[name="lastName"]');
  const nicInput = document.querySelector('input[name="nic"]');
  const emailInput = document.querySelector('input[name="email"]');
  const passwordInput = document.getElementById('password');
  const confirmPasswordInput = document.getElementById('confirm-password');
  const requirements = document.querySelectorAll('.requirement');
  const requirementsBox = document.querySelector('.password-requirements');

  // Track fields that need real-time validation
  const needsRealTimeValidation = new Set();

  // Track if password field has been blurred (showed error) before
  let passwordFieldHadError = false;

  // Initial state
  submitBtn.disabled = true;
  submitBtn.classList.add('disabled');

  // ===== VALIDATION FUNCTIONS =====
  function checkFormValidity() {
      const allFieldsFilled = [firstNameInput, lastNameInput, nicInput, emailInput, passwordInput, confirmPasswordInput]
          .every(input => input.value.trim() !== '');
      
      const allFieldsValid = 
          isNameValid(firstNameInput.value) &&
          isNameValid(lastNameInput.value) &&
          isNICValid(nicInput.value) &&
          isEmailValid(emailInput.value) &&
          isPasswordValid(passwordInput.value) &&
          (confirmPasswordInput.value === passwordInput.value);
      
      submitBtn.disabled = !(allFieldsFilled && allFieldsValid);
      submitBtn.classList.toggle('disabled', !(allFieldsFilled && allFieldsValid));
  }

  function isNameValid(name) {
      return /^[A-Za-z]+( [A-Za-z]+)*$/.test(name);
  }

  function isNICValid(nic) {
      return /^\d{8}$/.test(nic);
  }

  function isEmailValid(email) {
    return email.endsWith('@tbs.u-tunis.tn') || email.endsWith('@gmail.com');
}

  function isPasswordValid(password) {
      return password.length >= 8 &&
             /[A-Z]/.test(password) &&
             /[a-z]/.test(password) &&
             /[0-9]/.test(password) &&
             /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
  }

  function validatePassword(password, showError = false) {
    const requirements = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /[0-9]/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    // Update each requirement's visual state
    Object.entries(requirements).forEach(([requirement, met]) => {
      const element = document.querySelector(`[data-requirement="${requirement}"]`);
      if (element) {
        element.style.color = met ? 'green' : 'red';
        element.innerHTML = `${met ? '✓' : '✗'} ${element.textContent.replace(/[✓✗]\s*/, '')}`;
        
        // Add or remove fulfilled class
        if (met) {
          element.classList.add('fulfilled');
        } else {
          element.classList.remove('fulfilled');
        }
      }
    });

    // Show/hide error message below the password field only if showError is true
    const passwordGroup = passwordInput.closest('.input-group');
    const errorMsg = passwordGroup.querySelector('.field-message');
    
    if (showError && password && !Object.values(requirements).every(Boolean)) {
      errorMsg.textContent = 'Password does not meet requirements';
      errorMsg.style.display = 'block';
      passwordInput.classList.add('error');
    } else {
      errorMsg.textContent = '';
      errorMsg.style.display = 'none';
      passwordInput.classList.remove('error');
    }

    return Object.values(requirements).every(Boolean);
  }

  function validateNameField(input) {
    // Only format on blur
    const formattedValue = input.value
        .replace(/[^a-zA-Z\s]/g, '')  // Remove non-letters
        .replace(/\s+/g, ' ')         // Collapse multiple spaces
        .trim()                       // Trim whitespace
        .toLowerCase()
        .replace(/(^|\s)\S/g, char => char.toUpperCase());
    
    input.value = formattedValue;
  }

  function validateNIC() {
      nicInput.value = nicInput.value.replace(/\D/g, '').slice(0, 8);
      const isValid = isNICValid(nicInput.value);
      markFieldValidation(nicInput, isValid, 'Must be exactly 8 digits');
  }

  function validateEmail() {
      const isValid = isEmailValid(emailInput.value);
      markFieldValidation(emailInput, isValid, 'Must end with @tbs.u-tunis.tn');
  }

  function validatePassword() {
      const password = passwordInput.value;
      const isValid = isPasswordValid(password);
      
      // Only show error if field had error before
      if (passwordFieldHadError) {
          markFieldValidation(passwordInput, isValid, 'Password does not meet requirements');
      }
      
      // Update requirement indicators
      requirements.forEach(req => {
          const type = req.dataset.requirement;
          let fulfilled = false;
          
          switch(type) {
              case 'length': fulfilled = password.length >= 8; break;
              case 'uppercase': fulfilled = /[A-Z]/.test(password); break;
              case 'lowercase': fulfilled = /[a-z]/.test(password); break;
              case 'number': fulfilled = /[0-9]/.test(password); break;
              case 'special': fulfilled = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password); break;
          }
          
          req.classList.toggle('fulfilled', fulfilled);
      });

      // Hide requirements if all are fulfilled
      if (isValid) {
          requirementsBox.classList.remove('visible');
      }
  }

  function validateConfirmPassword() {
      const isValid = confirmPasswordInput.value === passwordInput.value;
      const inputGroup = confirmPasswordInput.closest('.input-group');
      
      if (!isValid && confirmPasswordInput.value.trim() !== '') {
          // Add error class to input but not to input-group
          confirmPasswordInput.classList.add('error');
          inputGroup.classList.remove('error');
          
          const messageDiv = inputGroup.querySelector('.field-message');
          messageDiv.textContent = 'Passwords do not match';
          messageDiv.style.display = 'block';
      } else {
          confirmPasswordInput.classList.remove('error');
          inputGroup.classList.remove('error');
          
          const messageDiv = inputGroup.querySelector('.field-message');
          messageDiv.textContent = '';
          messageDiv.style.display = 'none';
      }
  }

  function markFieldValidation(input, isValid, errorMessage) {
      const inputGroup = input.closest('.input-group');
      const messageDiv = inputGroup.querySelector('.field-message');
      
      if (!isValid && input.value.trim() !== '' && needsRealTimeValidation.has(input)) {
          inputGroup.classList.add('error');
          messageDiv.textContent = errorMessage;
          messageDiv.style.display = 'block';
      } else {
          inputGroup.classList.remove('error');
          messageDiv.textContent = '';
          messageDiv.style.display = 'none';
      }
  }

  // ===== EVENT LISTENERS =====
  // Name fields - allow typing anything, only validate/format on blur
  [firstNameInput, lastNameInput].forEach(input => {
      input.addEventListener('blur', function() {
          validateNameField(this);
          checkFormValidity();
      });
  });
  
  // NIC field - only validate after first blur
  nicInput.addEventListener('input', function() {
      this.value = this.value.replace(/\D/g, '').slice(0, 8);
      if (needsRealTimeValidation.has(this)) {
          validateNIC();
      }
      checkFormValidity();
  });
  nicInput.addEventListener('blur', function() {
      needsRealTimeValidation.add(this);
      validateNIC();
      checkFormValidity();
  });
  
  // Email field - only validate on blur
  emailInput.addEventListener('blur', function() {
      needsRealTimeValidation.add(this);
      validateEmail();
      checkFormValidity();
  });
  
  // Password field
  passwordInput.addEventListener('focus', function() {
    requirementsBox.classList.add('visible');
    requirementsBox.style.display = 'block';
  });
  
  passwordInput.addEventListener('blur', function() {
    requirementsBox.classList.remove('visible');
    requirementsBox.style.display = 'none';
    passwordFieldHadError = !isPasswordValid(this.value);
    needsRealTimeValidation.add(this);
    validatePassword(this.value, true);
    checkFormValidity();
  });
  
  passwordInput.addEventListener('input', function() {
    // Always validate password requirements on input
    validatePassword(this.value, false);
    
    if (needsRealTimeValidation.has(this)) {
      validatePassword(this.value, false);
    }
    checkFormValidity();
  });
  
  // Confirm password field
  confirmPasswordInput.addEventListener('input', function() {
    const password = passwordInput.value;
    const confirmPassword = this.value;
    const inputGroup = this.closest('.input-group');
    
    // Only update the visual state (red border) without showing error message
    if (confirmPassword && password !== confirmPassword) {
      this.classList.add('error');
      // Remove the input-group error class to prevent double styling
      inputGroup.classList.remove('error');
    } else {
      this.classList.remove('error');
    }
    
    if (needsRealTimeValidation.has(this)) {
      validateConfirmPassword();
    }
    checkFormValidity();
  });
  
  confirmPasswordInput.addEventListener('blur', function() {
    const password = passwordInput.value;
    const confirmPassword = this.value;
    const inputGroup = this.closest('.input-group');
    const msgDiv = inputGroup.querySelector('.field-message');
    
    if (confirmPassword && password !== confirmPassword) {
      msgDiv.textContent = 'Passwords do not match';
      msgDiv.style.display = 'block';
      this.classList.add('error');
      // Remove the input-group error class to prevent double styling
      inputGroup.classList.remove('error');
    } else {
      msgDiv.textContent = '';
      msgDiv.style.display = 'none';
      this.classList.remove('error');
    }
    
    needsRealTimeValidation.add(this);
    validateConfirmPassword();
    checkFormValidity();
  });

  // Real-time form validation
  setInterval(checkFormValidity, 300);

  // Initial check
  checkFormValidity();
  
  // Registration modal functionality
  const registerBtn = document.getElementById('register-btn');
  const registrationModal = document.getElementById('registration-modal');
  const modalOverlay = document.getElementById('modal-overlay');
  const closeBtn = document.getElementById('modal-close-btn');
  const regForm = document.getElementById('registration-form');
  const successMsg = document.getElementById('success-message');
  
  registerBtn.addEventListener('click', () => {
    registrationModal.classList.remove('hidden');
    modalOverlay.classList.remove('hidden');
    successMsg.textContent = '';
    successMsg.classList.remove('show');
    // Reset password validation on modal open
    validatePassword('', false);
    // Clear any error messages
    document.querySelectorAll('.field-message').forEach(msg => {
      msg.textContent = '';
      msg.style.display = 'none';
    });
    document.querySelectorAll('.input-group input').forEach(input => {
      input.classList.remove('error');
    });
  });

  closeBtn.addEventListener('click', closeModal);
  
  function closeModal() {
    registrationModal.classList.add('hidden');
    modalOverlay.classList.add('hidden');
  }

  regForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Clear previous messages
    document.querySelectorAll('.field-message').forEach(msg => {
      msg.textContent = '';
      msg.style.display = 'none';
    });
    document.querySelectorAll('.input-group input').forEach(input => {
      input.classList.remove('error');
    });
    successMsg.textContent = '';
    successMsg.classList.remove('show');

    const formData = new FormData(regForm);
    const payload = Object.fromEntries(formData.entries());

    try {
      const res = await fetch('/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const result = await res.json();

      if (res.ok) {
        // Only show the popup notification, not the inline message
        regForm.reset();
        
        // Show notification
        showNotification('Registration successful! Please check your email to confirm your account before logging in.', 'success');
        
        // Close the modal after a short delay
        setTimeout(() => {
          closeModal();
        }, 2000);
      } else {
        if (result.errors) {
          for (const [field, messages] of Object.entries(result.errors)) {
            const input = regForm.querySelector(`[name="${field}"]`);
            const inputGroup = input?.closest('.input-group');
            const msgDiv = inputGroup?.querySelector('.field-message');

            if (msgDiv && input) {
              msgDiv.textContent = messages.join(', ');
              msgDiv.style.display = 'block';
              input.classList.add('error');
            }
          }
        } else {
          successMsg.textContent = result.message || 'Error during registration.';
          successMsg.classList.add('show');
          successMsg.style.color = 'red';
        }
      }
    } catch (error) {
      console.error('Error:', error);
      successMsg.textContent = 'An unexpected error occurred.';
      successMsg.classList.add('show');
      successMsg.style.color = 'red';
    }
  });

  const toggles = document.querySelectorAll('.toggle-password');
  toggles.forEach(toggle => {
    toggle.addEventListener('click', () => {
      const input = document.getElementById(toggle.dataset.target);
      input.type = input.type === 'password' ? 'text' : 'password';
    });
  });
  
  // Login modal functionality
  const loginModal = document.getElementById('login-modal');
  const loginBtn = document.getElementById('login-btn');
  const closeLoginBtn = document.getElementById('login-close-btn');
  const loginForm = document.getElementById('login-form');
  const loginError = document.getElementById('login-error');
  const loginEmailInput = loginForm.querySelector('input[name="email"]');
  const loginPasswordInput = loginForm.querySelector('input[name="password"]');
  
  // Show modal
  loginBtn.addEventListener('click', () => {
    loginModal.classList.remove('hidden');
    modalOverlay.classList.remove('hidden');
    loginError.classList.remove('show');
    loginError.textContent = '';
    switchToLogin();
  });
  
  // Hide modal
  function hideLoginModal() {
    loginModal.classList.add('hidden');
    modalOverlay.classList.add('hidden');
    switchToLogin();
  }
  
  closeLoginBtn.addEventListener('click', hideLoginModal);
  
  // Clear error when user starts typing
  loginEmailInput.addEventListener('input', () => {
    loginError.classList.remove('show');
    loginError.textContent = '';
    loginEmailInput.classList.remove('error');
  });
  
  loginPasswordInput.addEventListener('input', () => {
    loginError.classList.remove('show');
    loginError.textContent = '';
    loginPasswordInput.classList.remove('error');
  });
  
  // Submit login
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    loginError.classList.remove('show');
    
    // Reset any error styling
    loginEmailInput.classList.remove('error');
    loginPasswordInput.classList.remove('error');
    
    const formData = new FormData(loginForm);
    const email = formData.get('email');
    const password = formData.get('password');
    
    // Client-side validation
    if (!email && !password) {
      loginError.textContent = 'Please provide your credentials';
      loginError.classList.add('show');
      loginEmailInput.classList.add('error');
      loginPasswordInput.classList.add('error');
      return;
    } else if (!email) {
      loginError.textContent = 'Please enter your email';
      loginError.classList.add('show');
      loginEmailInput.classList.add('error');
      return;
    } else if (!password) {
      loginError.textContent = 'Please enter your password';
      loginError.classList.add('show');
      loginPasswordInput.classList.add('error');
      return;
    }
    
    // Email format validation
    if (email && !email.includes('@')) {
      loginError.textContent = 'Please enter a valid email address';
      loginError.classList.add('show');
      loginEmailInput.classList.add('error');
      return;
    }
    
    try {
      const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Redirect based on the role returned by the backend
        window.location.href = data.redirect_url;
      } else {
        loginError.textContent = data.message;
        loginError.classList.add('show');
        
        // If the error is about email confirmation, highlight the email field
        if (data.message && data.message.includes('confirm your email')) {
          loginEmailInput.classList.add('error');
        }
      }
    } catch (err) {
      loginError.textContent = 'Login failed. Try again.';
      loginError.classList.add('show');
    }
  });

  /* ===== Forgot password flow ===== */
  const forgotLink = document.getElementById('forgot-password-link');
  const forgotContainerElement = document.getElementById('forgot-container');
  const loginFormElement = document.getElementById('login-form');
  const modalTitle = document.getElementById('login-modal-title');
  const fpSendBtnEl = document.getElementById('fp-send-btn');
  const fpResetBtnEl = document.getElementById('fp-reset-btn');
  const fpStep1El = document.getElementById('fp-step1');
  const fpStep2El = document.getElementById('fp-step2');
  const fpMessageEl = document.getElementById('fp-message');
  const backToLoginEl = document.getElementById('back-to-login-link');

  function switchToForgot() {
    loginFormElement.style.display = 'none';
    forgotContainerElement.style.display = 'block';
    modalTitle.textContent = 'Reset Password';
    fpMessageEl.textContent = '';
    fpMessageEl.style.color = '';
  }

  function switchToLogin() {
    loginFormElement.style.display = 'block';
    forgotContainerElement.style.display = 'none';
    modalTitle.textContent = 'Login';
    fpMessageEl.textContent = '';
  }

  forgotLink.addEventListener('click', (e) => {
    e.preventDefault();
    switchToForgot();
  });

  backToLoginEl.addEventListener('click', (e) => {
    e.preventDefault();
    switchToLogin();
  });

  // Step 1: request code
  fpSendBtnEl.addEventListener('click', async () => {
    const email = fpStep1El.querySelector('input[type="email"]').value.trim();
    const nationalId = fpStep1El.querySelector('input[type="text"]').value.trim();

    if (!email || !nationalId) {
      fpMessageEl.textContent = 'Please fill in all fields';
      fpMessageEl.style.color = 'red';
      return;
    }

    fpSendBtnEl.disabled = true;
    fpMessageEl.textContent = 'Sending reset code...';
    fpMessageEl.style.color = 'black';

    try {
      const res = await fetch('/password-reset/initiate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, national_id: nationalId })
      });
      const data = await res.json();
      if (data.success) {
        fpMessageEl.style.color = 'green';
        fpMessageEl.textContent = data.message;
        fpStep1El.style.display = 'none';
        fpStep2El.style.display = 'block';
      } else {
        fpMessageEl.style.color = 'red';
        fpMessageEl.textContent = data.message || 'Error sending reset code';
        fpSendBtnEl.disabled = false;
      }
    } catch (err) {
      fpMessageEl.style.color = 'red';
      fpMessageEl.textContent = 'An unexpected error occurred';
      fpSendBtnEl.disabled = false;
    }
  });

  // Step 2: reset password
  fpResetBtnEl.addEventListener('click', async () => {
    const email = fpStep1El.querySelector('input[type="email"]').value.trim();
    const code = fpStep2El.querySelector('input[type="text"]').value.trim();
    const newPassword = fpStep2El.querySelector('input[type="password"]').value.trim();
    const confirmPassword = fpStep2El.querySelectorAll('input[type="password"]')[1].value.trim();

    if (!code || !newPassword || !confirmPassword) {
      fpMessageEl.style.color = 'red';
      fpMessageEl.textContent = 'Please fill in all fields';
      return;
    }
    if (newPassword !== confirmPassword) {
      fpMessageEl.style.color = 'red';
      fpMessageEl.textContent = 'Passwords do not match';
      return;
    }

    fpResetBtnEl.disabled = true;
    fpMessageEl.textContent = 'Resetting password...';
    fpMessageEl.style.color = 'black';

    try {
      const res = await fetch('/password-reset/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, code, new_password: newPassword })
      });
      const data = await res.json();
      if (data.success) {
        fpMessageEl.style.color = 'green';
        fpMessageEl.textContent = data.message;
        fpResetBtnEl.disabled = true;
        setTimeout(() => {
          hideLoginModal();
        }, 2000);
      } else {
        fpMessageEl.style.color = 'red';
        fpMessageEl.textContent = data.message || 'Error resetting password';
        fpResetBtnEl.disabled = false;
      }
    } catch (err) {
      fpMessageEl.style.color = 'red';
      fpMessageEl.textContent = 'An unexpected error occurred';
      fpResetBtnEl.disabled = false;
    }
  });
});