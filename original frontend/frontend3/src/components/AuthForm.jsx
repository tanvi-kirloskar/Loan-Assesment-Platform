import { useState } from "react";
import { login, register, saveAccessToken, ApiError } from "../services/api";

const initialValues = { email: "", password: "" };

function validate(values) {
  const errors = {};

  if (!values.email.trim()) {
    errors.email = "Email is required.";
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email.trim())) {
    errors.email = "Enter a valid email address.";
  }

  if (!values.password) {
    errors.password = "Password is required.";
  }

  return errors;
}

export default function AuthForm({ onAuthSuccess, notice }) {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  const isLogin = mode === "login";

  function handleChange(field, value) {
    setValues((prev) => ({ ...prev, [field]: value }));
  }

  function handleBlur(field) {
    setTouched((prev) => ({ ...prev, [field]: true }));
    setErrors(validate({ ...values }));
  }

  function switchMode() {
    setMode(isLogin ? "register" : "login");
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setFormError(null);
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const validationErrors = validate(values);
    setErrors(validationErrors);
    setTouched({ email: true, password: true });

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      const authFn = isLogin ? login : register;
      const { access_token } = await authFn(
        values.email.trim(),
        values.password
      );

      saveAccessToken(access_token);
      onAuthSuccess();
    } catch (error) {
      if (error instanceof ApiError) {
        setFormError(error.message);
      } else {
        setFormError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="auth-card">
      <p className="auth-eyebrow">Secure Sign In</p>

      {notice && (
        <div className="submit-error" role="alert">
          {notice}
        </div>
      )}

      <div className="auth-tabs" role="tablist" aria-label="Authentication mode">
        <button
          type="button"
          role="tab"
          aria-selected={isLogin}
          className={`auth-tab ${isLogin ? "auth-tab-active" : ""}`}
          onClick={() => mode !== "login" && switchMode()}
        >
          Log In
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={!isLogin}
          className={`auth-tab ${!isLogin ? "auth-tab-active" : ""}`}
          onClick={() => mode !== "register" && switchMode()}
        >
          Register
        </button>
      </div>

      <p className="auth-subtitle">
        {isLogin
          ? "Log in to continue to your loan application."
          : "Create an account to start a loan application."}
      </p>

      {formError && (
        <div className="submit-error" role="alert">
          {formError}
        </div>
      )}

      <form className="application-form" onSubmit={handleSubmit} noValidate>
        <div className="form-field">
          <label htmlFor="auth-email">Email</label>
          <input
            id="auth-email"
            type="email"
            value={values.email}
            onChange={(e) => handleChange("email", e.target.value)}
            onBlur={() => handleBlur("email")}
            aria-invalid={touched.email && !!errors.email}
            aria-describedby={errors.email ? "auth-email-error" : undefined}
            placeholder="you@example.com"
            autoComplete="email"
          />
          {touched.email && errors.email && (
            <p className="field-error" id="auth-email-error">
              {errors.email}
            </p>
          )}
        </div>

        <div className="form-field">
          <label htmlFor="auth-password">Password</label>
          <input
            id="auth-password"
            type="password"
            value={values.password}
            onChange={(e) => handleChange("password", e.target.value)}
            onBlur={() => handleBlur("password")}
            aria-invalid={touched.password && !!errors.password}
            aria-describedby={
              errors.password ? "auth-password-error" : undefined
            }
            placeholder="••••••••"
            autoComplete={isLogin ? "current-password" : "new-password"}
          />
          {touched.password && errors.password && (
            <p className="field-error" id="auth-password-error">
              {errors.password}
            </p>
          )}
        </div>

        <button type="submit" className="submit-button" disabled={isSubmitting}>
          {isSubmitting
            ? isLogin
              ? "Logging in…"
              : "Registering…"
            : isLogin
            ? "Log In"
            : "Register"}
        </button>
      </form>

      <p className="auth-switch">
        {isLogin ? "Don't have an account? " : "Already have an account? "}
        <button type="button" className="auth-switch-link" onClick={switchMode}>
          {isLogin ? "Register" : "Log in"}
        </button>
      </p>
    </div>
  );
}
