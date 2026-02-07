"use client";

import { useState, useEffect } from "react";
import axios from "axios";

export default function OnboardingPage() {
  const [step, setStep] = useState(1);
  const [phone, setPhone] = useState("");
  const [sendStatus, setSendStatus] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [verified, setVerified] = useState(false);
  const [estName, setEstName] = useState("");
  const [address, setAddress] = useState("");
  const [siret, setSiret] = useState("");
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const next = () => setStep((s) => Math.min(5, s + 1));
  const prev = () => setStep((s) => Math.max(1, s - 1));

  // Fetch current user's phone if present
  useEffect(() => {
    try {
      const token = localStorage.getItem("jwt_token");
      if (!token) return;
      // Optionally fetch /me to get phone
      axios.get(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/me`, { headers: { Authorization: `Bearer ${token}` } })
        .then((r) => setPhone(r.data.phone || ""))
        .catch(() => {});
    } catch (e) {}
  }, []);

  const sendVerification = async () => {
    setLoading(true);
    setSendStatus(null);
    try {
      const resp = await axios.post(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/send-verification-code`, { phone });
      setSendStatus(resp.data.message || "Code sent");
    } catch (e: any) {
      setSendStatus(e?.response?.data?.detail || "Failed to send code");
    } finally {
      setLoading(false);
    }
  };

  const verifyCode = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const resp = await axios.post(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/verify-phone-code`, { phone, code });
      setVerified(true);
      next();
    } catch (e: any) {
      setMessage(e?.response?.data?.detail || "Invalid code");
    } finally {
      setLoading(false);
    }
  };

  const submit = async () => {
    setLoading(true);
    setMessage(null);
    try {
      if (!verified) {
        setMessage("Please verify your phone before continuing");
        setLoading(false);
        return;
      }
      const token = localStorage.getItem("jwt_token");
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const resp = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/onboarding/complete`,
        { establishment_name: estName, address, siret },
        { headers }
      );
      const estId = resp.data.establishment_id;
      // Upload logo if provided
      if (logoFile) {
        const form = new FormData();
        form.append("file", logoFile);
        await axios.post(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/establishments/${estId}/logo`, form, { headers: { ...headers, "Content-Type": "multipart/form-data" } });
      }
      setMessage("Onboarding finalized successfully");
      next();
    } catch (e: any) {
      setMessage(e?.response?.data?.detail || "Failed to complete onboarding");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4">Onboarding wizard</h1>

      <div className="mb-4">Step {step} / 4</div>

      {step === 1 && (
        <div>
          <h2 className="font-medium">Welcome</h2>
          <p className="mb-4">Let's set up your farm profile.</p>
          <button className="btn btn-primary" onClick={next}>Start</button>
        </div>
      )}

      {step === 2 && (
        <div>
          <h2 className="font-medium">Phone verification</h2>
          <div className="space-y-2 mt-3">
            <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="Phone (+40...)" className="input" />
            <div className="flex gap-2">
              <button className="btn" onClick={sendVerification} disabled={!phone || loading}>Send code</button>
              <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="Enter code" className="input" />
              <button className="btn btn-primary" onClick={verifyCode} disabled={!code || loading}>Verify</button>
            </div>
            {sendStatus && <div className="text-sm text-gray-500">{sendStatus}</div>}
            {message && <div className="text-sm text-red-600">{message}</div>}
          </div>
          <div className="mt-4">
            <button className="btn" onClick={prev}>Back</button>
            <button className="btn btn-primary ml-3" onClick={next} disabled={!verified}>Next</button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div>
          <h2 className="font-medium">Establishment details</h2>
          <div className="space-y-2 mt-3">
            <input value={estName} onChange={(e) => setEstName(e.target.value)} placeholder="Farm name" className="input" />
            <input value={address} onChange={(e) => setAddress(e.target.value)} placeholder="Address" className="input" />
            <input value={siret} onChange={(e) => setSiret(e.target.value)} placeholder="SIRET (optional)" className="input" />
          </div>
          <div className="mt-4">
            <button className="btn" onClick={prev}>Back</button>
            <button className="btn btn-primary ml-3" onClick={next}>Next</button>
          </div>
        </div>
      )}

      {step === 4 && (
        <div>
          <h2 className="font-medium">Upload logo (optional)</h2>
          <div className="space-y-2 mt-3">
            <input type="file" onChange={(e) => setLogoFile(e.target.files?.[0] ?? null)} className="input" />
          </div>
          <div className="mt-4">
            <button className="btn" onClick={prev}>Back</button>
            <button className="btn btn-primary ml-3" onClick={submit} disabled={loading}>
              {loading ? "Submitting..." : "Finish onboarding"}
            </button>
          </div>
        </div>
      )}

      {step === 5 && (
        <div>
          <h2 className="font-medium">All set!</h2>
          <p className="mb-4">{message || "Onboarding complete."}</p>
        </div>
      )}
      {message && <div className="mt-4 text-sm text-red-600">{message}</div>}
    </div>
  );
}
